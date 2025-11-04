import time
from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, Any, Optional

from core.hardware import AdbClient


class Checker(ABC):
    """
        Abstract class for all checkers.
        To create your own checker you need to import this interface
        and make check function and init method, if you need it.
        This method will be processed after object initialization.
    """

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
            :param adb: hardware client like a context for make a check.
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
            if not checkingResult: return None

            return function(*args, **kwargs)

        return wrapper



# few pre-installed checkers

class BaseChecker(Checker):
    """ Base and empty checker """

    def init(self): pass
    def check(self, adb: AdbClient) -> bool: pass



class WaitingChecker(Checker):
    """
        Checker, which let action wait till task returns True.
        You can configure it via config method.
        Config method takes 2 arguments - waiterFunction and delay, which is 1 second by default.
        Delay let script wait before new check.
        Waiter function needs to return bool and take adb client object.
    """

    waiterFunction: Optional[Callable[[AdbClient], bool]]
    delay: int = 1

    def init(self): pass

    @classmethod
    def config(cls, waiterFunction: Callable[[AdbClient], bool], delay: int=1) -> None:
        cls.waiterFunction = waiterFunction
        cls.delay = delay


    def check(self, adb: AdbClient) -> bool:
        while True:
            if self.waiterFunction:
                if self.waiterFunction(adb): return True

            time.sleep(self.delay)
