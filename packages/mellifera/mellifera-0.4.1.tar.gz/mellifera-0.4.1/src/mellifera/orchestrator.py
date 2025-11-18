from __future__ import annotations

from abc import ABC, abstractmethod
from types import SimpleNamespace
import functools
import logging

from typing import TYPE_CHECKING, Any, Optional
import threading

from mellifera.executor import Executor
from mellifera.services import TrioService, NSMainThreadService
from mellifera.service import ServiceState
import trio.lowlevel

if TYPE_CHECKING:
    from mellifera.service import Service


class Orchestrator:

    def __init__(self) -> None:
        self.logger = logging.getLogger("calsiprovis.orchestrator.Orchestrator")
        self.services = dict()
        self.system_nursery = None
        self.service_nursery = None
        self.trio_token = None
        self.running = False
        self.to_run = []

        self.write_channel, self.recv_channel = trio.open_memory_channel(1000)

        from mellifera.executors import TrioExecutor, HAS_NSMAINTHREAD
        if HAS_NSMAINTHREAD:
            from mellifera.executors import NSMainThreadExecutor

        self.trio = TrioExecutor(self)
        if HAS_NSMAINTHREAD:
            self.mainthread_executor = NSMainThreadExecutor(self)
        else:
            self.mainthread_executor = None

    def get_service(self, name: str) -> Service:
        if name in self.services:
            return self.services[name]
        else:
            raise ValueError(f"Service with name `{name}` not found")

    def register_service(self, service: Service, name: str) -> None:
        match service:
            case TrioService():
                service.register(self, self.trio, name)
            case NSMainThreadService():
                if not self.mainthread_executor:
                    raise ValueError("Cannot have a main_thread_service without a main thread executor")
                service.register(self, self.mainthread_executor, name)
            case _:
                raise ValueError(f"Cannot handle service of type {type(service)}")
        self.services[name] = service

    def start_service(self, service: Service | str) -> None:
        if isinstance(service, str):
            service = self.get_service(service)
        match service:
            case TrioService():
                if service.state == ServiceState.REGISTERED:
                    service.state = ServiceState.WILL_BE_STARTED
                    if self.service_nursery:
                        self.service_nursery.start_soon(self.trio.run_service, service)
                    else:
                        self.to_run.append(service)
            case NSMainThreadService():
                if service.state == ServiceState.REGISTERED:
                    if not self.mainthread_executor:
                        raise ValueError("Cannot have a main_thread_service without a main thread executor")
                    service.state = ServiceState.WILL_BE_STARTED
                    self.mainthread_executor.start_service(service)
            case _:
                raise ValueError(f"Cannot start service of type {type(service)}")

    def stop_service(self, service: Service | str) -> None:
        if isinstance(service, str):
            service = self.get_service(service)
        if service.state.value < ServiceState.STOPPING.value:
            match service:
                case TrioService():
                    self.service_nursery.start_soon(self.trio.stop_service, service)
                case NSMainThreadService():
                    if self.mainthread_executor and self.mainthread_executor.service == service:
                        self.mainthread_executor.stop()
                    else:
                        raise ValueError(f"Cannot start service of type {type(service)}, mainthread_executor not active")
                case _:
                    raise ValueError(f"Cannot start service of type {type(service)}")

    def enable_service(self, service: Service, name: str) -> None:
        self.register_service(service, name)
        self.start_service(service)

    def run_async_function(self, async_function):
        if not self.trio_token:
            raise ValueError("Trying to run async function, but trio is not started yet")
        async def closure():
            await self.write_channel.send(async_function)
        trio.from_thread.run(closure, trio_token=self.trio_token)

    async def wait_for_mainthread(self):
        await trio.sleep(0)
        if self.mainthread_executor and self.mainthread_executor.service:
            await self.mainthread_executor.service.shutdown

    async def process_messages(self):
        with self.recv_channel:
            async with trio.open_nursery() as nursery:
                nursery.start_soon(self.wait_for_mainthread)
                async for async_function in self.recv_channel:
                    async def closure():
                        try:
                            await async_function()
                        except Exception:
                            self.logger.error("Wild async function raised an error", exc_info=True)
                    nursery.start_soon(closure)

    def stop(self):
        self.write_channel.close()

    def run(self):
        self.logger.info('Orchestrator.run starting')
        if self.mainthread_executor:
            self.start_sync()
            self.mainthread_executor.run_sync()
        else:
            self.run_sync()
        self.logger.info('Orchestrator.run ending')

    def start_sync(self):
        self.logger.debug("Starting in sync mode")
        self.thread = threading.Thread(target=trio.run, args=(self.run_async,), daemon=False)
        self.thread.start()

    def run_sync(self):
        trio.run(self.run_async)

    async def run_async(self):
        self.thread = threading.current_thread()
        self.trio_token = trio.lowlevel.current_trio_token()
        self.logger.debug('run started')
        async with trio.open_nursery() as system_nursery:
            self.logger.debug('nursery opened')
            self.system_nursery = system_nursery
            system_nursery.start_soon(self.process_messages)
            if self.mainthread_executor:
                self.mainthread_executor.trio_startup.set()
            async with trio.open_nursery() as service_nursery:
                self.service_nursery = service_nursery
                service_nursery.start_soon(self.wait_for_mainthread)
                for service in self.to_run:
                    self.service_nursery.start_soon(self.trio.run_service, service)
                self.to_run = []
            self.stop()
        self.logger.info("Nursery of mellifera.executors.TrioExecutor.run closed")

    def stop_all(self):
        for service in self.services.values():
            self.stop_service(service)
