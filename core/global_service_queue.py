import os
import uuid
import time
from typing import Any, Optional
import multiprocessing
from multiprocessing.connection import Connection

from core.middleware import afterLoad
from core.service import IService
from core.exceptions import *
from meta.singleton import Singleton



class Worker:
    '''
        Worker - one physic core loader,
        Process all tasks at the same time on one core via asyncio
        If service has no tasks al all - remove from the queue automatically
        Worker works only with active services
    '''

    def __init__(self, iteratorDelay: float=0.05):
        # WORKER CONFIGS AND PARAMS
        self._iteratorDelay = iteratorDelay
        # worker ID
        self._id: str = str(uuid.uuid4())

        # iterator lifetime controller. Turn it on while starting and turn off with deleting worker.
        # DO NOT TOUCH NOWHERE EXCEPT THAT
        self._isAlive: bool = False

        # main list with all process tasks
        # (key) serviceID : Service (value)
        # YOU CAN CHANGE IT ONLY IN ITERATOR TO AVOID SYNC PROBLEMS
        self._services: dict[str, IService] = {}
        # pipe for control workers (get workers calls and return calls result)
        self._pipe: Optional[Connection] = None

    def __del__(self):
        try: self._del()
        except: pass

    @property
    def id(self) -> str: return self._id

    @property
    def workerPrefix(self) -> str:
        """
            Like group name for workers process
        """
        return 'Worker'

    def _del(self) -> None:
        """
            Worker destructor. Use via kill calls and BrokenPipe errors.
        """

        # kill worker and all services
        for service in list(self._services.values()):
            self._killService(service)

        try:
            self._pipe.send(('done', []))
            # waiting for send finish
            time.sleep(self._iteratorDelay * 10)
            self._pipe.close()
        except (BrokenPipeError, OSError): pass

        # stop iterator
        self._isAlive = False
        # terminate worker process, if its in worker process
        if multiprocessing.current_process() \
            .name.startswith(self.workerPrefix): os._exit(0)


    def _callProcessor(self, name: str, *args):
        # TODO: All worker calls
        match name:
            case 'stop': self._del()
            case 'add':
                processServices = list(self._services.keys())

                for service in args:
                    if isinstance(service, IService) and service.id not in processServices:
                        # adding service
                        self._addService(service)

                self._sendToPipe(('done', []))
            case 'count':
                self._sendToPipe(('count', [len(self._services)]))

    def _callsInterrupter(self) -> None:
        """
            Interrupt iterator if any call received.
        """

        try:
            if self._pipe.poll(timeout=self._iteratorDelay / 2):
                call: tuple[str, tuple|list] = self._pipe.recv()
                self._callProcessor(call[0], *call[1])
        except (BrokenPipeError, OSError): self._del()


    def _sendToPipe(self, data: Any) -> None:
        try: self._pipe.send(data)
        except (BrokenPipeError, OSError): self._del()


    def _killService(self, service: IService) -> None:
        service.kill()
        del self._services[service.id]

    def _addService(self, service: IService) -> None:
        self._services[service.id] = service


    def _iterator(self, ):
        if not self._pipe: raise UnableToDo('Cannot start workers iterator without pipe.')

        while self._isAlive:
            time.sleep(self._iteratorDelay)

            # calls processor
            self._callsInterrupter()

            # services starter
            for serviceId in list(self._services.keys()):
                service = self._services[serviceId]

                # do not touch already started services
                if service.isWorking: continue

                # delete if service has no tasks and not working
                if service.loadedTasksCount == 0:
                    self._killService(service)

                # starting if it has task(s) and not already started
                print('Starting service', service)
                # service.start starts new thread, works fine with IO bound tasks
                service.start()


    def start(self, workerPipe: Connection):
        """
            You need to set pipe from the main process to avoid process isolation problems.
        """
        # its new process, isolated, because iterator blocks the process/thread
        self._pipe = workerPipe
        self._isAlive = True
        self._iterator()




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
        self._isLoaded = False

        # workers list, to control workers wia Worker ID and workers calls
        # contains workers pipes, which are used to make workers calls
        self._workersConnections: dict[str, Connection] = {}

        # table with all workers processes
        # use it to save and terminate processes
        self._workersProcesses: dict[str, multiprocessing.Process] = {}


    @property
    def isLoaded(self) -> bool: return self._isLoaded

    @property
    @afterLoad
    def workersCount(self) -> int: return len(self._workersConnections)

    @afterLoad
    def _workerCall(self, _id: str, call: str, *args: Any) -> Optional[tuple[str, list[Any]]]:
        connection = self._workersConnections.get(_id)
        if not connection: raise NotFoundException('Connection not found.')

        try:
            connection.send((call, args))

            # receiving data
            if not connection.poll(timeout=1): raise BrokenPipeError
            fb, data = connection.recv()

            if fb: return fb, data
        except (BrokenPipeError, OSError, ValueError): pass

        return None

    @afterLoad
    def _getLessLoadedWorker(self) -> str:
        """
            Get count of processing tasks/services from every worker.
            And then return id of the less loaded worker.
            Returns ID of the worker.
        """
        # getting services count
        result: dict[int, str] = {} # format: count_of_services - worker id

        for serviceId, serviceConnection in self._workersConnections.items():
            callResult: Optional[tuple[str, list[int]]] = self._workerCall(serviceId, 'count')
            if callResult is None: continue

            if callResult[0] == 'count':
                result[callResult[1][0]] = serviceId

        return result[min(result)]

    def _loadService(self, service: IService) -> bool:
        # TODO: this
        workerId = self._getLessLoadedWorker()
        result: Optional[tuple[str, Any]] = self._workerCall(workerId, 'add', service)

        if result is None: return False
        if result[0] != 'done': return False
        return True


    @afterLoad
    def add(self, *args) -> None:
        """
            Add service or services to the less loaded worker.
        """
        for arg in args: self._loadService(arg)

    @afterLoad
    def remove(self, service: IService) -> None:
        # TODO: Finish remove method for removing services
        pass


    def load(self) -> None:
        """
            Manage all workers, create and start them.
            You need to call this method before any other actions.
        """

        # workers generator
        if self._max_units > multiprocessing.cpu_count():
            raise NotEnoughCores('MAX_UNITS must be less then actual core`s count!')
        if self._max_units <= 0:
            raise UnableToDo('Cannot start workers - self._max_units cannot be less then 1.')

        for _ in range(self._max_units):
            worker = Worker()

            # create worker`s connection
            # parentPipe - for GSM, childPipe - for worker
            parentPipe, childPipe = multiprocessing.Pipe()
            self._workersConnections[worker.id] = parentPipe

            # DO NOT USE DAEMON PROCESSES WITH FORK CONTEXT - YOU CANNOT USE ASYNC WITH THEM
            workerProcess = self._context.Process(
                target=worker.start, args=(childPipe,), name=f"{worker.workerPrefix}_{worker.id}"
            )
            workerProcess.start()

        self._isLoaded = True


    def kill(self) -> None:
        # TODO: MAKE KILLER FOR ALL WORKERS PROCESS (via terminate)
        pass