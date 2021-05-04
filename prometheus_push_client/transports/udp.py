import asyncio
import socket

from prometheus_push_client import compat


class BaseUdpTransport:

    def __init__(self, host, port, mtu=500, datagram_lines=25):
        self.host = host
        self.port = int(port)
        self.transport = None
        self._mtu = mtu
        self._datagram_lines = datagram_lines

    def stop(self):
        self.transport.close()

    def pack_datagrams(self, iterable):
        datagram = []
        datagram_size = 0
        for line in iterable:
            if (
                len(datagram) == self._datagram_lines or
                len(line) + datagram_size >= self._mtu
            ):
                yield b"\n".join(datagram)
                datagram.clear()
                datagram_size = 0

            datagram.append(line)
            datagram_size += len(line)

        if datagram:
            yield b"\n".join(datagram)

    def push_all(self, iterable):
        for data in self.pack_datagrams(iterable):
            self.push_one(data)

    def push_one(self, data):
        raise NotImplementedError()


# TODO: crashes on creation time DNS errors -- retry?


class SyncUdpTransport(BaseUdpTransport):
    def start(self):
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def push_one(self, data):
        self.transport.sendto(data, (self.host, self.port))


class AioUdpTransport(BaseUdpTransport):
    async def start(self, loop=None):
        loop = loop or compat.get_running_loop()
        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: asyncio.DatagramProtocol(),
            remote_addr=(self.host, self.port)
        )

    async def stop(self):
        super().stop()

    async def push_all(self, iterable):
        super().push_all(iterable)

    def push_one(self, data):
        self.transport.sendto(data)