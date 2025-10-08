import asyncio
import queue
import threading
import uuid
from multiprocessing.pool import worker
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
        Worker works only with active services
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


    def _deleteService(self, service: IService) -> None:
        service.kill()
        del self._services[service.id]

    async def _iterator(self):
        while True:
            await asyncio.sleep(self._iteratorDelay)

            # adder/remover for new
            for s2add in self._getFromQueue(self._servicesToAdd):
                self._services[s2add.id] = s2add

            for s2rem in self._getFromQueue(self._servicesToRemove):
                self._deleteService(s2rem)


            # services starter
            for serviceId in list(self._services.keys()):
                service = self._services[serviceId]

                # do not touch already started services
                if service.isWorking: continue

                # delete if service has no tasks and not working
                if service.loadedTasksCount == 0:
                    self._deleteService(service)

                # starting if it has task(s) and not already started
                print('Starting service', service)
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

        self._servicesToAdd.put( service )

    def remove(self, service: IService) -> None:
        if service.id in list(self._services.keys()):
            self._servicesToRemove.put( service )

    def get(self) -> None:
        raise UnableToDo('Cannot get service from Worker of GSQ! Use SERVICES TABLE instead.')

    @property
    def size(self) -> int: # get loaded services
        return len(self._services)



class GlobalServiceManager:
    '''
        Manager for all CoreWorkers (1 core = 1 worker).
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
        # changing process creating method
        self._context = multiprocessing.get_context("fork")
        self._max_units = max_units

        # table with workers addrs for every service
        # service.id : service_worker
        self._servicesQueue: dict[str, Worker] = {} # NEEDS ONLY FOR REMOVING AND ADDING SERVICES IN WORKERS

        # workers lists
        self._workers: list[Worker] = []
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
        raise UnableToDo('Cannot get size from GlobalServiceManager')

    @property
    def workersCount(self) -> int: return len(self._workers)

    @property
    def startedWorkersCount(self) -> int: return len(self._workersProcesses)


    def _onlyAfterLoad(self) -> None:
        if not self._isLoaded: raise GSMNotLoaded()


    def _getLessLoadedWorker(self) -> Worker:
        return min(self._workers, key=lambda w: w.size)

    def _loadService(self, service: IService) -> None:
        llw: Worker = self._getLessLoadedWorker()
        llw.add(service)
        self._servicesQueue[service.id] = llw


    def add(self, *args) -> None:
        """
            Add service to the less loaded worker.
        """
        self._onlyAfterLoad()
        if len(args) == 1: self._loadService(*args)
        else:
            for arg in args: self._loadService(arg)


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
                # DO NOT USE DAEMON PROCESSES WITH FORK CONTEXT - YOU CANNOT USE ASYNC WITH THEM
                self._context.Process(target=worker.start)
            )

        self._startWorkers()
        self._isLoaded = True

    def kill(self) -> None:
        # TODO: MAKE KILLER FOR ALL WORKERS PROCESS (via terminate)
        pass