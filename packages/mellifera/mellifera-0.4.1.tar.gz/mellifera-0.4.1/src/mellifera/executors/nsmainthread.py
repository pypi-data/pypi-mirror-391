try:
    from Foundation import NSThread
    from libdispatch import dispatch_async, dispatch_sync, dispatch_get_main_queue
except ModuleNotFoundError:
    raise ModuleNotFoundError("To use mellifera.orchestrators.nsmainthread you need to have pyobjc installed and run on macos")

import signal

from types import SimpleNamespace
import logging
import threading
import functools

from mellifera.orchestrator import Orchestrator
from mellifera.services.nsmainthread import NSMainThreadService
from mellifera.service import Service
from mellifera.executor import Executor

from mellifera.service import ServiceState

def threadsafe(f):
    @functools.wraps(f)
    def inner(self, *args, **kwargs):
        return self.run_threadsafe(f, self, *args, **kwargs)

    return inner

class NSMainThreadExecutor(Executor):
    requires_run = True

    def __init__(self, orchestrator) -> None:
        self.orchestrator = orchestrator
        self.service = None
        self.logger = logging.getLogger("mellifera.executors.NSMainThreadExecutor")
        self.thread = None
        self.trio_startup = threading.Event()
        self._start_service = False

    def run_threadsafe(self, f, *args, **kwargs):
        if self.thread is None or self.thread == threading.current_thread():
            r = f(*args, **kwargs)
            return None
        else:
            def closure():
                self.logger.debug(f'excecuted closure of {f.__name__} threadsafe via NSMainThreadExecutor')
                return f(*args, **kwargs)
            queue = dispatch_get_main_queue()
            r = dispatch_async(queue, closure)
            return None

    def run_exposed(self, service, f, *args, **kwargs):
        return self.run_threadsafe(f, service, *args, **kwargs)

    def start_service(self, service: Service) -> None:
        assert isinstance(service, NSMainThreadService)
        if self.service == service:
            self._start_service = True
        else:
            raise ValueError("Asked to start {service}, but registered {self.service}")

    @threadsafe
    def stop(self) -> None:
        self.service.stop()

    def wait_for_trio_startup(self) -> None:
        self.trio_startup.wait()

    def run_sync(self) -> None:
        self.thread = threading.current_thread()
        self.wait_for_trio_startup()
        try:
            self.logger.debug("Starting up")
            if self.service and self._start_service:
                try:
                    try:
                        self.logger.debug("Constructing service")
                        self.service.construct()
                        self.logger.debug("Initializing service")
                        self.service.init_sync()
                        self.logger.debug("Running service")
                        self.service.run_sync()
                        self.logger.debug("Running service done, stopping")
                    finally:
                        self.orchestrator.stop_all()
                finally:
                    self.service.finalize_sync()
        finally:
            self.running = False
