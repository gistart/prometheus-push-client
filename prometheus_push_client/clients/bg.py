import asyncio
import threading
import time

from prometheus_push_client import compat


class BackgroundClient:

    def __init__(self, format, transport, period=15.0, *args, **kwargs):
        self.format = format
        self.transport = transport
        self.period = float(period)
        self.stop_event = None

        self._period_step = 0.5  # check event every 0.5 seconds

        super().__init__(*args, **kwargs)

    def sleep_steps_iter(self, period):
        n_full_steps, last_step = divmod(period, self._period_step)
        for _ in range(int(n_full_steps)):
            yield self._period_step
        if last_step > 0:
            yield last_step


class ThreadBGClient(BackgroundClient, threading.Thread):
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
            samples_iter = self.format.iter_samples()
            try:
                self.transport.push_all(samples_iter)
            except Exception:
                pass  # TODO log?
            period = self.period - (time.time() - ts_start)


class AsyncioBGClient(BackgroundClient):
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
            samples_iter = self.format.iter_samples()
            try:
                await self.transport.push_all(samples_iter)
            except Exception:
                pass  # TODO: log?
            period = self.period - (time.time() - ts_start)