import time
from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, Any, Optional



class AdbChecker(ABC):
    """
        Abstract class for all pre action checkers.
        Pre action method - method, which will processed before the adb action.
        To create your own checker you need to import this interface
        and make check function and init method, if you need it.
        This method will be processed after object initialization.
    """

    def __init__(self, adb):
        """ :param adb: AdbClient instance. """
        self.adb = adb
        self.init()
        self.adbArgs: tuple = ()
        self.adbKwargs: dict[str, Any] = {}

    def init(self, *args, **kwargs) -> None:
        """ Unnecessary method, if you need more initialization arguments or attributes. """
        self._args = args
        self._kwargs = kwargs


    @classmethod
    @abstractmethod
    def check(self, adb, *args, **kwargs) -> bool:
        """
            Checking function, used in "checkable" decorator.
            :param adb: hardware client like a context for make a check.
            :return: True or False - checking result.
        """
        pass


def adbCheckable(function: Callable) -> Callable:
    """
        Decorator to make functions "checkable".
        Function will be processed if check function returns True.
    """


    @wraps(function)
    def wrapper(adbClient, *args, **kwargs) -> Any:
        checker = adbClient.checker
        checkingResult = checker.check(checker.adb, *checker.adbArgs, **checker.adbKwargs)
        if not checkingResult: return checkingResult

        return function(adbClient, *args, **kwargs)

    return wrapper



# few pre-installed checkers

class BaseAdbChecker(AdbChecker):
    """ Base and empty checker """
    def check(self, _, **kw) -> bool: pass



class WaitingAdbChecker(AdbChecker):
    """
        AdbChecker, which let action wait till task returns True.
        You can configure it via config method.
        Config method takes 2 arguments - waiterFunction and delay, which is 1 second by default.
        Delay let script wait before new check.
        Waiter function needs to return bool and take adb client object.
    """

    waiterFunction: Optional[Callable[[Any], bool]]
    delay: int = 1

    @classmethod
    def config(cls, waiterFunction: Callable[[Any], bool], delay: int=1) -> None:
        cls.waiterFunction = waiterFunction
        cls.delay = delay


    def check(self, adb, *_, **_kw) -> bool:
        while True:
            if self.waiterFunction:
                if self.waiterFunction(adb): return True

            time.sleep(self.delay)
