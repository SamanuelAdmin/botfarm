from core.service import IService
from core.exceptions import *
from meta.queue import IQueue
from meta.singleton import Singleton


class GlobalServiceQueue(IQueue, metaclass=Singleton):
    '''
        Queue for controlling all services processes.
        Main for the core, only one in the program.
        Name - GSQ

        All what you put to init is GSQ configs.

        1 unit = 1 task per momnet
    '''

    def __init__(self, max_units: int):
        self._max_units = max_units
        self._servicesQueue: list[IService] = []


    @property
    def size(self) -> int:
        return len(self._servicesQueue)

    def add(self, service: IService) -> None:
        self._servicesQueue.append(service)

    def get(self) -> None:
        raise UnableToDo('Cannot get service from GSQ! Use SERVICES TABLE instead.')

    def remove(self, service: IService) -> None:
        self._servicesQueue.remove(service)

    def _taskProcessor(self) -> None:
        pass

    def start(self) -> None:
        '''
            IN NEW THREAD.
            Starts task processor
        '''
        pass