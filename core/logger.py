from datetime import datetime
from typing import Any, Generator

from core.core_configurator import CoreConfigurator
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
        return f'{dateTimeSubsting}  [{self._type}]  {"".join(self.info)}'



class Logger(IQueue):
    __metaclass__ = Singleton

    def __init__(self):
        self._logsList: list[Log] = []

    def add(self, log: Log):
        print(log)
        self._logsList.append(log)

    def get(self) -> Log: return self._logsList.pop(0)

    @property
    def size(self) -> int: return len(self._logsList)

    def getAll(self) -> Generator[Log, Any, None]:
        while self.size > 0:
            yield self.get()

    def makeEmpty(self) -> None:
        self._logsList.clear()
