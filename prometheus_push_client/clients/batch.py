import asyncio
import threading
import time
import logging

from prometheus_push_client import compat


log = logging.getLogger("prometheus.batch")


class BaseBatchClient:
    def __init__(self, format, transport, period=15.0, *args, **kwargs):
        self.format = format
        self.transport = transport
        self.period = float(period)
        self.stop_event = None

        self._period_step = 0.25  # check event every 0.25 seconds

        super().__init__(*args, **kwargs)

    def sleep_steps_iter(self, period):
        n_full_steps, last_step = divmod(period, self._period_step)
        for _ in range(int(n_full_steps)):
            yield self._period_step
        if last_step > 0:
            yield last_step


class ThreadBatchClient(BaseBatchClient, threading.Thread):
    def start(self):
        self.stop_event = threading.Event()
        self.transport.start()
        super().start()

    def stop(self):
        self.stop_event.set()
        try:
            self.join()
        finally:
            self.transport.stop()

    def run(self):
        period = self.period

        while not self.stop_event.is_set():
            for step in self.sleep_steps_iter(period):
                time.sleep(step)
                if self.stop_event.is_set():
                    break

            ts_start = time.time()
            data_gen = self.format.iter_samples()
            try:
                self.transport.push_all(data_gen)
            except Exception:
                log.error("push crashed", exc_info=True)
            period = self.period - (time.time() - ts_start)


class AsyncBatchClient(BaseBatchClient):
    async def start(self):
        self.stop_event = asyncio.Event()
        await self.transport.start()
        self._runner = compat.create_task(self.run())

    async def stop(self):
        self.stop_event.set()
        try:
            await asyncio.wait([self._runner])
        finally:
            await self.transport.stop()

    async def run(self):
        period = self.period

        while not self.stop_event.is_set():
            for step in self.sleep_steps_iter(period):
                try:
                    await asyncio.sleep(step)
                except asyncio.CancelledError:
                    self.stop_event.set()
                if self.stop_event.is_set():
                    break

            ts_start = time.time()
            data_gen = self.format.iter_samples()
            try:
                await self.transport.push_all(data_gen)
            except Exception:
                log.error("push crashed", exc_info=True)
            period = self.period - (time.time() - ts_start)