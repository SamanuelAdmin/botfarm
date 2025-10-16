"""

Structure:
Logger <- LoggerQueue <- Log(s)
Logger (singleton), has all interface for simply adding logs.
LoggerQueue - saver for all logs (in-memory database), for using
with admin panel, inner modules etc.
Log(s) - log object, for simple formating, saving etc.

Logger must be inheritance from ILogger (interface with all "logger methods")!
Logger logic:
1) adding logger by "endpoint" - info, error, warning etc.
2) process information by function decorator
3) endpoint returns only Log object for current log.
4) adding log to the queue
5) process gotten log with every handler (processor)

"""
import threading
from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
from typing import Any, Generator, Callable, Optional, Iterable

from meta.queue import IQueue
from meta.singleton import Singleton



class Log:
    def __init__(
            self, _type: str, *info,
            setDatetime: bool=True,
            logTypes: tuple=('info', 'debug', 'warning', 'error', 'critical'),
    ):
        self.info: tuple = info
        self._type = _type
        self._setDatetime = setDatetime

        if self._type not in logTypes:
            self._type = 'info'

    def _getDatetime(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        dateTimeSubsting: str = self._getDatetime() + ' ' if self._setDatetime else ''
        return f'{dateTimeSubsting}  [{self._type}]  {" ".join(self.info)}'



class LoggerQueue(IQueue):
    __metaclass__ = Singleton

    def __init__(self):
        self._logsList: list[Log] = []

    def add(self, log: Log):
        self._logsList.append(log)

    def get(self) -> Log: return self._logsList.pop(0)

    @property
    def size(self) -> int: return len(self._logsList)

    def getAll(self) -> Generator[Log, Any, None]:
        """
            Getting all logs and drain the queue.
        """
        while self.size > 0:
            yield self.get()

    def makeEmpty(self) -> None:
        self._logsList.clear()



class ILogger(ABC):
    """
        Interface for logger classes.
        All custom logger must use this interface.
    """
    _loggerQueue: IQueue
    _lock: threading.Lock # threads safety mechanic

    @abstractmethod
    def info(self, info: str): pass
    @abstractmethod
    def warning(self, info: str): pass
    @abstractmethod
    def error(self, info: str): pass
    @abstractmethod
    def critical(self, info: str): pass
    @abstractmethod
    def debug(self, info: str): pass



LOG_HANDLER_CONTRACT = Callable[[Log], None]


class Logger(ILogger):
    __metaclass__ = Singleton
    _logsHandlers: list[LOG_HANDLER_CONTRACT] = []
    _lock: threading.Lock

    def __init__(
            self, setDatetime: bool=True,
            logsHandler: Optional[Iterable[LOG_HANDLER_CONTRACT]]=None ):
        self._setDatetime = setDatetime
        self._loggerQueue = LoggerQueue()
        self.addLogHandler(*logsHandler if logsHandler else [])
        self._lock = threading.Lock()


    @classmethod
    def addLogHandler(cls, *logHandlers: LOG_HANDLER_CONTRACT) -> None:
        for logHandler in logHandlers:
            cls._logsHandlers.append(logHandler)


    def logsConverter(function: Callable[[ILogger, *tuple[Any]], None]) -> Callable:
        """
            Behavior of all log methods.
            Just change this part if you need to change logger logic.
        """

        @wraps(function)
        def wrapper(logger: ILogger, *args: tuple[Any]):
            convertedArgs: str = ' '.join( [ str(obj) for obj in args ] )
            log = function(logger, convertedArgs)

            with logger._lock:
                logger._loggerQueue.add(log)

            # process logs
            for handler in logger._logsHandlers:
                handler(log)

        return wrapper


    @logsConverter
    def info(self, info: str):
        return Log( 'info', info, setDatetime=self._setDatetime )

    @logsConverter
    def debug(self, info: str):
        return Log( 'debug', info, setDatetime=self._setDatetime )

    @logsConverter
    def warning(self, info: str):
        return Log( 'warning', info, setDatetime=self._setDatetime )

    @logsConverter
    def error(self, info: str):
        return Log( 'error', info, setDatetime=True )

    @logsConverter
    def critical(self, info: str):
        return Log( 'critical', info, setDatetime=True )




# adding base handlers
def consoleHandler(log: Log):
    print(log)


def setup_default_logger():
    Logger.addLogHandler(consoleHandler)