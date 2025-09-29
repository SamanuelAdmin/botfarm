'''
Queue for controlling all services processes.
Main for the core, only one in the program.
Name - GSQ
'''

from core.service import IService
from core.exceptions import *
from meta.queue import IQueue
from meta.singleton import Singleton


class GlobalServiceQueue(IQueue, metaclass=Singleton):
    @property
    def size(self) -> int: self.

    def __init__(self):
        pass

    def add(self, service: IService): pass

    def get(self) -> None:
        raise UnableToDo('Cannot get service from GSQ! Use SERVICES TABLE instead.')

