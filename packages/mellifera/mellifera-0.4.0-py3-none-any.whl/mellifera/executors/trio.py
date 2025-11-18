from typing import TYPE_CHECKING

import trio
import trio.lowlevel
import threading
import inspect
import logging
from queue import Queue
from types import SimpleNamespace

from mellifera.services.trio import TrioService, ServiceState
from mellifera.orchestrator import Orchestrator
from mellifera.service import Service
from mellifera.executor import Executor


class TrioExecutor(Executor):
    requires_run = False

    def __init__(self, orchestrator) -> None:
        self.orchestrator = orchestrator
        self.services = []
        self.logger = logging.getLogger("mellifera.executors.TrioExecutor")

        self.nursery = None
        self.to_start = []
        self.stopped = trio.Event()

    def run_exposed(self, f, service, *args, **kwargs):
        if threading.current_thread() == self.orchestrator.thread:
            return f(service, *args, **kwargs)
        else:
            if inspect.iscoroutinefunction(f):
                async def closure():
                    return await f(service, *args, **kwargs)
            else:
                async def closure():
                    return f(service, *args, **kwargs)
            self.orchestrator.run_async_function(closure)

    async def stop_service(self, service):
        try:
            with trio.fail_after(5):
                await service.stop()
                await service.stopped
        except trio.TooSlowError:
            with trio.move_on_after(10):
                await service.cancel()

    async def _run_service(self, service):
        try:
            service.construct()
        except Exception as e:
            self.logger.error(f"Error during construction of service {service.name}", exc_info=True)
            self.orchestrator.stop_all()
            raise e

        try:
            self.logger.debug(f'Initializing service {service.name}')
            await service.init()
            self.logger.debug(f'Initializing service {service.name} DONE')
        except Exception as e:
            self.logger.error(f"Error during initialisation of service {service.name}", exc_info=True)
            self.orchestrator.stop_all()
            raise e

        try:
            self.logger.debug(f'Running service {service.name}')
            await service.run()
            self.logger.debug(f'Running service {service.name} DONE')
        except Exception as e:
            self.logger.error(f"Error during run of service {service.name}", exc_info=True)
            self.orchestrator.stop_all()
            raise e

    async def run_service(self, service):
        try:
            async with trio.open_nursery() as nursery:
                service.nursery = nursery
                await self._run_service(service)
        finally:
            self.logger.debug(f"Finalizing {service.name}")
            with trio.CancelScope(shield=True):
                await service.finalize()
            self.logger.debug(f"Finalizing {service.name} done")
