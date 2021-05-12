import asyncio
import socket
import logging

from prometheus_push_client import compat


log = logging.getLogger("prometheus.udp")


class BaseUdpTransport:
    def __init__(self, host, port, mtu=508, datagram_lines=25):
        self.host = host
        self.port = int(port)
        self.transport = None
        self._mtu = mtu
        self._datagram_lines = datagram_lines

    def stop(self):
        self.transport.close()

    def pack_datagrams(self, iterable):
        datagram = []
        datagram_bytes = 0
        for line in iterable:
            if len(datagram) != 0:  # first line always goes
                if (
                    len(datagram) == self._datagram_lines or
                    len(line) + datagram_bytes > self._mtu
                ):
                    yield b"\n".join(datagram)
                    datagram.clear()
                    datagram_bytes = 0

            datagram.append(line)
            datagram_bytes += len(line) + 1  # newline!

        if len(datagram):
            yield b"\n".join(datagram)

    def push_all_sync(self, iterable):
        for data in self.pack_datagrams(iterable):
            self.push_one(data)

    def push_one(self, data):
        try:
            return self.transport.sendto(data, (self.host, self.port))
        except socket.gaierror:  # name resolution error
            pass


# TODO: ipv6 support?


class SyncUdpTransport(BaseUdpTransport):
    def start(self):
        self._getaddrinfo()
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    push_all = BaseUdpTransport.push_all_sync

    def _getaddrinfo(self):
        try:
            return socket.getaddrinfo(
                self.host,
                self.port,
                family=socket.AF_INET,
                type=socket.SOCK_DGRAM,
            )
        except socket.gaierror as e:
            log.error("%s -- %s:%s", e, self.host, self.port)


class AioUdpTransport(BaseUdpTransport):
    async def start(self, loop=None):
        loop = loop or compat.get_running_loop()
        await self._getaddrinfo(loop)
        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: asyncio.DatagramProtocol(),
            family=socket.AF_INET,
            allow_broadcast=False,
        )

    async def stop(self):
        super().stop()

    async def push_all(self, iterable):
        self.push_all_sync(iterable)

    async def _getaddrinfo(self, loop):
        try:
            return await loop.getaddrinfo(
                self.host,
                self.port,
                family=socket.AF_INET,
                type=socket.SOCK_DGRAM,
            )
        except socket.gaierror as e:
            log.error("%s -- %s:%s", e, self.host, self.port)