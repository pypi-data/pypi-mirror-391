from abc import ABC, abstractmethod

from mellifera.service import Service

class Executor(ABC):

    @abstractmethod
    def run_exposed(self, f, service, *args, **kwargs):
        """Run function f in service with args and kwargs in a threadsafe matter

        This function is threadsafe.
        """
        ...
