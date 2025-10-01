import asyncio
import queue
import threading
import uuid
from typing import Any, Callable, Generator

import multiprocessing

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
        # creating in main GSM process so I can initialize queue here
        self._servicesToAdd: multiprocessing.Queue = multiprocessing.Queue()
        self._servicesToRemove: multiprocessing.Queue = multiprocessing.Queue()

        self._iteratorDelay = iteratorDelay


    def _getFromQueue(self, q) -> Generator[Any, None, None]:
        while True:
            try:
                # if q.empty(): break ! DO NOT USE - ITS UNSTABLE, USE EXCEPTIONS INSTEAD
                yield q.get_nowait()
            except queue.Empty: break


    async def _iterator(self):
        while True:
            await asyncio.sleep(self._iteratorDelay)

            # adder/remover for new
            for s2add in self._getFromQueue(self._servicesToAdd):
                self._services[s2add[0]] = s2add[1]

            for s2rem in self._getFromQueue(self._servicesToRemove):
                s2rem[1].kill()
                del self._services[s2rem[0]]

            # clear adder and remover lists
            # self._servicesToAdd.clear()
            # self._servicesToRemove.clear()

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

        # self._servicesToAdd.append( (service.id, service) )
        self._servicesToAdd.put( (service.id, service) )

    def remove(self, service: IService) -> None:
        if service.id in list(self._services.keys()):
            # self._servicesToRemove.append( (service.id, service) )
            self._servicesToRemove.put( (service.id, service) )

    def get(self) -> None:
        raise UnableToDo('Cannot get service from Worker of GSQ! Use SERVICES TABLE instead.')

    @property
    def size(self) -> int: # get loaded services
        return len(self._services)



class GlobalServiceManager(IQueue):
    '''
        Manager for all CoreWorkers (1 core = 1 worker).
        Queue for controlling all services processes.
        Main for the core, only one in the program.
        Name - GSM
        This entity just distribute resources between services.
        It doesn't control services!!!

        Scheme:
        GSM - ServiceQueue - less loaded worker - async started task

        1 unit = 1 core loaded by workers
        (1 unit = 1 started worker)
    '''

    __metaclass__ = Singleton

    def __init__(self, max_units: int):
        self._max_units = max_units
        self._workers: list[Worker] = []

        # table with workers addrs for every service
        # service.id : service_worker
        self._servicesQueue: dict[str, Worker] = {}
        self._workersProcesses: list[multiprocessing.Process] = []

        self._isLoaded = False


    def _startWorkers(self):
        # all processes magic
        # worker generator
        if len(self._workers) == 0: raise UnableToDo('Cannot start workers - workers not found.')

        for wp in self._workersProcesses:
            wp.start()


    @property
    def size(self) -> int:
        return len(self._servicesQueue)

    def _onlyAfterLoad(self) -> None:
        if not self._isLoaded: raise GSMNotLoaded()


    def _getLessLoadedWorker(self) -> Worker:
        return min(self._workers, key=lambda w: w.size)

    def _loadService(self, service: IService) -> None:
        llw: Worker = self._getLessLoadedWorker()
        llw.add(service)
        self._servicesQueue[service.id] = llw

    def add(self, *args: tuple[IService]) -> None:
        self._onlyAfterLoad()
        if len(args) == 1:
            return self._loadService(*args)

        for arg in args: self._loadService(arg)
        return


    def get(self) -> None:
        raise UnableToDo('Cannot get service from GSM! Use SERVICES TABLE instead.')

    def remove(self, service: IService) -> None:
        self._onlyAfterLoad()
        serviceWorker = self._servicesQueue.get(service.id)
        if not serviceWorker: return

        serviceWorker.remove(service)


    def load(self) -> None:
        '''
            Manage all workers, create and start them.
            You need to call this method before any other actions.
        '''

        # workers generator
        if self._max_units > multiprocessing.cpu_count():
            raise NotEnoughCores('MAX_UNITS must be less then actual core`s count!')

        for _ in range(self._max_units):
            worker = Worker()
            self._workers.append( worker )
            # daemon = True -> processes will be killed with GSM
            self._workersProcesses.append(
                multiprocessing.Process(target=worker.start, daemon=True)
            )

        self._startWorkers()
        self._isLoaded = True

