import asyncio
import threading
import uuid
from typing import Any, Callable

from core.service import IService
from core.exceptions import *
from meta.queue import IQueue
from meta.singleton import Singleton



class Worker(IQueue):
    '''
        Worker - one physic core loader,
        Process all tasks at the same time on one core via asyncio
        If service has no tasks al all - remove from the queue automatically
    '''

    def __init__(self, iteratorDelay: float=0.05):
        # main list with all started tasks
        # (key) serviceID : Service (value)
        # YOU CAN CHANGE IT ONLY IN ITERATOR TO AVOID SYNC PROBLEMS
        self._services: dict[str, IService] = {}
        # worker ID
        self._id: str = str(uuid.uuid4())
        # add and remove list to sync adding and removing with iterator
        self._servicesToAdd: list[tuple[str, IService]] = []
        self._servicesToRemove: list[tuple[str, IService]] = []


    async def _iterator(self):
        while True:
            # adder/remover for new
            for s2add in set(self._servicesToAdd):
                self._services[s2add[0]] = s2add[1]

            for s2rem in set(self._servicesToRemove):
                s2rem[1].kill()
                del self._services[s2rem[0]]

            # clear adder and remover lists
            self._servicesToAdd.clear()
            self._servicesToRemove.clear()

            # services starter
            for serviceId in list(self._services.keys()):
                service = self._services[serviceId]

                # do not touch already started services
                if service.isWorking: continue

                # delete if service has no tasks and not working
                if service.loadedTasksCount == 0:
                    del self._services[serviceId]

                # starting if it has task(s) and not already started
                asyncio.create_task(service.start())


    def start(self):
        # its new process, isolated
        asyncio.run(self._iterator())

    def add(self, service: IService) -> None:
        # do not add if service has no tasks in it
        if service.loadedTasksCount == 0: return
        # and if service is not already in queue
        if service.id in list(self._services.keys()):
            raise ServiceAlreadyInWork()

        self._servicesToAdd.append( (service.id, service) )

    def remove(self, service: IService) -> None:
        if service.id in list(self._services.keys()):
            self._servicesToRemove.append( (service.id, service) )

    def get(self) -> None:
        raise UnableToDo('Cannot get service from Worker of GSQ! Use SERVICES TABLE instead.')

    @property
    def size(self) -> int: # get current workers
        return len(self._services)



class GlobalServiceManager(IQueue):
    '''
        Manager for all CoreWorkers (1 core = 1 worker).
        Queue for controlling all services processes.
        Main for the core, only one in the program.
        Name - GSM

        Scheme:
        GSM - ServiceQueue - less loaded worker - async started task

        1 unit = 1 core loaded by workers
        (1 unit = 1 started worker)
    '''

    __metaclass__ = Singleton

    def __init__(self, max_units: int):
        self._max_units = max_units
        self._workers: list[Worker] = []

        self._servicesQueue: list[IService] = []
        self._taskProcessorThread: threading.Thread

    def _startWorkers(self):
        # all processes magic
        pass

    @property
    def size(self) -> int:
        return len(self._servicesQueue)

    def add(self, *args: tuple[IService]) -> None:
        if len(args) == 1: self._servicesQueue.append(*args)
        else: self._servicesQueue.extend(args)

    def get(self) -> None:
        raise UnableToDo('Cannot get service from GSM! Use SERVICES TABLE instead.')

    def remove(self, service: IService) -> None:
        self._servicesQueue.remove(service)

    def makeEmpty(self):
        self._servicesQueue.clear()


    def start(self) -> None:
        '''
            Manage all workers, create and start
        '''
        self._startWorkers()

