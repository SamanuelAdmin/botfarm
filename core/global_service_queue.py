import os
import sys
import threading
import uuid
import time
from typing import Any, Optional, Callable
import multiprocessing
from multiprocessing.connection import Connection

from core.middleware import afterLoad
from core.logger import Logger
from core.service import IService
from core.exceptions import *
from meta.singleton import Singleton
from meta.stdout import IStdout


logger = Logger()

class WorkerStdout(IStdout):
    """
        Catching all worker`s (script`s) logs from stdout
        and process it with interrupt function.
        Use only in child process, NOT IN MAIN!
    """
    def __init__(self, interrupt: Callable):
        self._interrupt = interrupt
        self._baseStdout = sys.stdout
        sys.stdout = self

    def __del__(self):
        sys.stdout = sys.__stdout__ # restore previous stdout

    def write(self, *args: *tuple[str]) -> None:
        formatString = ' '.join(args).replace('\n', '')
        if len(formatString) == 0: return
        self._interrupt(formatString)

    def flush(self) -> None:
        self._baseStdout.flush()


class Worker:
    '''
        Worker - one physic core loader,
        Process all tasks at the same time on one core via asyncio
        If service has no tasks al all - remove from the queue automatically
        Worker works only with active services.
    '''

    def __init__(self, iteratorDelay: float=0.05):
        # WORKER CONFIGS AND PARAMS
        self._iteratorDelay = iteratorDelay
        # worker ID
        self._id: str = str(uuid.uuid4())
        self._customStdout: IStdout

        # pipe for sending logs to GSM logs handler
        self._logger: Connection

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

    @property
    def _loggerPrefix(self) -> str:
        return f'{self.workerPrefix}_{self.id}'


    def _sendLog(self, _type: str, info: str) -> None:
        """
            Sending logs from worker to GSM logs handler.
            Auto add worker`s prefix.
            Using example:
            self._sendLog( ('info', 'Worker started') )
        """

        try:
            self._logger.send( (_type, f'{self._loggerPrefix} {info}') )
        except (BrokenPipeError, OSError) as error: pass

    def _sendCaughtLog(self, text: str) -> None:
        """
            Function for sending logs to logs pipe instead of
            printing to console.
            Instead of sendLog function, this one cannot
            take any "type" attributes.
        """
        self._sendLog('info', text)


    def _del(self) -> None:
        """
            Worker destructor. Use via kill calls and BrokenPipe errors.
        """

        # kill worker and all services
        for service in list(self._services.values()):
            self._killService(service)
        self._sendLog('debug','All services killed.')

        try:
            self._pipe.send(('done', []))
            # waiting for send finish
            time.sleep(self._iteratorDelay * 10)
            self._pipe.close()
            self._sendLog('debug', 'Pipe closed.')
        except (BrokenPipeError, OSError) as error:
            self._sendLog('debug', f'Cannot close pipe. {error}')

        # stop iterator
        self._isAlive = False

        self._sendLog('info', 'Worker deleted!')
        # terminate worker process, if its in worker process
        if multiprocessing.current_process() \
            .name.startswith(self.workerPrefix): os._exit(0)


    def _callProcessor(self, name: str, *args):
        self._sendLog('debug', f'System call {name}. Arguments count: {len(args)}')
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
        except (BrokenPipeError, OSError, EOFError): self._del()


    def _sendToPipe(self, data: Any) -> None:
        try: self._pipe.send(data)
        except (BrokenPipeError, OSError, EOFError): self._del()


    def _killService(self, service: IService) -> None:
        service.kill()
        del self._services[service.id]
        self._sendLog('info', f'Service {service.id} killed.')

    def _addService(self, service: IService) -> None:
        self._services[service.id] = service


    def _iterator(self, ):
        if not self._pipe:
            self._sendLog('error', 'Cannot start workers iterator without pipe.')
            raise UnableToDo('Cannot start workers iterator without pipe.')

        # inner functions which needed only in iterator
        def checkIfServiceStarted(service: IService) -> bool:
            return any([service.isStarted, service.isWorking])


        self._sendLog('debug', 'Worker (iterator) started.')
        while self._isAlive:
            time.sleep(self._iteratorDelay)

            # calls processor
            self._callsInterrupter()

            # services starter
            for serviceId in list(self._services.keys()):
                service = self._services[serviceId]


                # starting if it has task(s) and not already started
                if not checkIfServiceStarted(service):
                    if service.loadedTasksCount == 0:
                        # delete if service has no tasks and not working
                        self._killService(service)
                    else:
                        # service.start starts new thread, works fine with IO bound tasks
                        service.start()
                        self._sendLog('debug', f'Process new task from service {serviceId}.')
                        continue


    def start(self, workerPipe: Connection, logger: Connection) -> None:
        """
            You need to set pipe from the main process to avoid process isolation problems.
        """
        self._logger = logger

        # its new process, isolated, because iterator blocks the process/thread
        self._pipe = workerPipe
        self._isAlive = True

        # creating custom stdout for new started worker
        self._customStdout = WorkerStdout(self._sendCaughtLog)

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

    def __init__(self, max_units: int, logsHandlerDelay: float=1):
        # changing process creating method
        self._context = multiprocessing.get_context("fork")
        self._max_units = max_units
        self._logsHandlerDelay = logsHandlerDelay
        self._isLoaded = False
        self._isAlive = True # DO NOT TOUCH IF YOU DONG KNOW WHAT YOU'RE DOING

        # workers list, to control workers wia Worker ID and workers calls
        # contains workers pipes, which are used to make workers calls
        self._workersConnections: dict[str, Connection] = {}
        self._workersLogsConnections: dict[str, Connection] = {}

        # table with all workers processes
        # use it to save and terminate processes
        self._workersProcesses: dict[str, multiprocessing.Process] = {}
        logger.debug('Initialized GlobalServiceManager.')



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

            if fb:
                logger.debug(f'Successfully worker call. ID: {_id}, Call: {call}, Args count: {len(args)}.')
                return fb, data
        except (BrokenPipeError, OSError, EOFError, ValueError): pass

        return None

    @afterLoad
    def _logsHandler(self):
        if len(self._workersLogsConnections) < 1:
            logger.error('Cannot start GSM workers logs handler. Logs connections less then 1.')
            raise UnableToDo('Cannot start GSM workers logs handler. Logs connections less then 1.')

        while self._isAlive:
            time.sleep(self._logsHandlerDelay)

            # use only with list(.keys) to avoid memory problems
            for workerId in list(self._workersLogsConnections.keys()):
                try:
                    logsConnection = self._workersLogsConnections[workerId]

                    if logsConnection.poll(timeout=self._logsHandlerDelay / self._max_units):
                        log: tuple[str, str] = logsConnection.recv()
                        if not isinstance(log, tuple) or len(log) != 2: continue

                        # process log, searching for logger`s func and then log the log
                        loggingFunc = getattr(logger, log[0], logger.debug)
                        loggingFunc( log[1] )

                except (BrokenPipeError, OSError, EOFError):
                    logger.debug(f'Logs connection with {workerId} closed. Removing from the table.')
                    del self._workersLogsConnections[workerId]



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

        if not result:
            logger.error('No alive workers found. Cannot get less loaded worker.')
            raise NotFoundException('No alive workers found.')

        return result[min(result)]


    def _loadService(self, service: IService) -> bool:
        workerId = self._getLessLoadedWorker()
        logger.debug(f'Adding new service to {workerId}...')
        result: Optional[tuple[str, Any]] = self._workerCall(workerId, 'add', service)
        logger.debug(f'Adding to {workerId} - {result}.')

        if result is None: return False
        if result[0] != 'done': return False
        return True


    @afterLoad
    def add(self, *args) -> None:
        """
            Add service or services to the less loaded worker.
        """
        results = [
            self._loadService(arg) for arg in args
        ]
        logger.info(f'Successfully added { len(list(filter(lambda x: x, results))) } services.')


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
            logger.critical('Cannot load GSM! MAX_UNITS must be less then actual core`s count!')
            raise NotEnoughCores('MAX_UNITS must be less then actual core`s count!')
        if self._max_units <= 0:
            logger.critical('Cannot load GSM! MAX_UNITS cannot be less then 1.')
            raise UnableToDo('Cannot start workers - self._max_units cannot be less then 1.')

        for _ in range(self._max_units):
            worker = Worker()

            # create worker`s connection
            # parentPipe - for GSM, childPipe - for worker
            controlParentPipe, controlChildPipe = multiprocessing.Pipe()
            self._workersConnections[worker.id] = controlParentPipe

            logsParentPipe, logsChildPipe = multiprocessing.Pipe()
            self._workersLogsConnections[worker.id] = logsParentPipe

            # DO NOT USE DAEMON PROCESSES WITH FORK CONTEXT - YOU CANNOT USE ASYNC WITH THEM
            workerProcess = self._context.Process(
                target=worker.start, args=(controlChildPipe, logsChildPipe), name=f"{worker.workerPrefix}_{worker.id}"
            )
            self._workersProcesses[worker.id] = workerProcess
            workerProcess.start()
            logger.debug(f'Starting worker {worker.id}...')

        logger.info('Global service manager started.')
        self._isLoaded = True

        # post loading
        logger.debug(f'Starting logs handler.')
        threading.Thread(target=self._logsHandler).start()


    def kill(self) -> bool:
        """
            Hard kill the workers. Terminate all processes.
            Use it only in "hard" situation.
        """
        logger.debug(f'Terminating (hard kill) all workers ({len(self._workersProcesses)})...')
        for process in list(self._workersProcesses.values()):
            process.terminate()

        logger.debug(f'Killed all workers - {len(self._workersConnections)} units. Closing GSM.')
        self._isAlive = False
        return True