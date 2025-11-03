from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, Any

from services.adb_manager import AdbClient


class Checker(ABC):
    def __init__(self, adb: AdbClient):
        self.adb: AdbClient = adb
        self.init()

    @abstractmethod
    def init(self, *args, **kwargs) -> None:
        """ Unnecessary method, if you need more initialization arguments or attributes. """
        pass

    @classmethod
    @abstractmethod
    def check(self, adb: AdbClient) -> bool:
        """
            Checking function, used in "checkable" decorator.
            :param adb: adb client like a context for make a check.
            :return: True or False - checking result.
        """
        pass

    def checkable(self, function: Callable) -> Callable:
        """
            Decorator to make functions "checkable".
            Function will be processed if check function returns True.
        """

        @wraps(function)
        def wrapper(*args, **kwargs) -> Any:
            checkingResult = self.check(self.adb)
            if not checkingResult: return

            return function(*args, **kwargs)

        return wrapper


class BaseChecker(Checker):
    def __init__(self, adb: AdbClient):
        self.adb = adb