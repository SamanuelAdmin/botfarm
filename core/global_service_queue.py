import enum
import os
import sys
import threading
import uuid
import time
from dataclasses import dataclass, field
from multiprocessing.pool import worker
from typing import Any, Optional, Callable
import multiprocessing
from multiprocessing.connection import Connection
from queue import Empty

from core.middleware import afterLoad
from core.logger import Logger
from core.service import IService, HistoryObject
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

    def write(self, *args) -> None:
        formatString = ' '.join(args).replace('\n', '')
        if len(formatString) == 0: return
        self._interrupt(formatString)

    def flush(self) -> None:
        self._baseStdout.flush()



class WorkerStatus(enum.IntEnum):
    OK_STATUS = 0
    ERROR_STATUS = 1

class WorkerEventTypes(enum.StrEnum):
    WORKER_STARTED = 'worker_started'
    WORKER_STOPPED = 'worker_stopped'
    SERVICE_STARTED = "service_started"
    SERVICE_FINISHED = "service_finished"
    SERVICE_ERROR = "service_error"

@dataclass
class WorkerEvent:
    workerId: str
    type: WorkerEventTypes
    serviceId: Optional[str] = None
    context: list = field(default_factory=list)
    def __str__(self): return f'[{self.workerId}] {self.serviceId} -> ({self.type}) {self.context}'

class WorkerCall(enum.StrEnum):
    WORKER_STOP = 'stop'
    SERVICE_ADD = 'add'
    SERVICE_REMOVE = 'remove'
    SERVICES_COUNT = 'count' # count of services is processing
    SERVICES = 'services' # get ids of services is processing
    SERVICE_CHECK = 'check_service' # check if service is processing
    SERVICE_HISTORY = 'service_history'



class Worker:
    '''
        Worker - one physic core loader,
        Process all tasks at the same time on one core via asyncio
        If service has no tasks al all - remove from the queue automatically
        Worker works only with active services.

        Have 2 connection methods - 2 pipes.
        Worker pipe (_controlPipe) - for getting commands and sending responses.
        Logs pipe (logger) - for logs only.
    '''

    def __init__(self, iteratorDelay: float=0.05):
        # WORKER CONFIGS AND PARAMS
        self._iteratorDelay = iteratorDelay
        # worker ID
        self._id: str = str(uuid.uuid4())
        self._customStdout: IStdout

        # pipe for sending logs to GSM logs handler
        self._logsPipe: Connection

        # iterator lifetime controller. Turn it on while starting and turn off with deleting worker.
        # DO NOT TOUCH NOWHERE EXCEPT THAT
        self._isAlive: bool = False

        # main list with all process tasks
        # (key) serviceID : Service (value)
        # YOU CAN CHANGE IT ONLY IN ITERATOR TO AVOID SYNC PROBLEMS
        self._services: dict[str, IService] = {}

        # pipes for manage worker
        self._controlPipe: Optional[Connection] = None # stdin analog (takes and process worker calls)
        # MUST BE QUEUE - safer and faster
        self._eventsPipe: Optional[multiprocessing.Queue] = None  # stdout analog (gives events messages)
        self._logsPipe: Optional[Connection] = None    # stderr analog (for any logs, LOGS ONLY)


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

        try: self._logsPipe.send((_type, f'{self._loggerPrefix} {info}'))
        except (BrokenPipeError, OSError) as error: pass

    def _sendCaughtLog(self, text: str) -> None:
        """
            Function for sending logs to logs pipe instead of
            printing to console.
            Instead of sendLog function, this one cannot
            take any "type" attributes.
        """
        self._sendLog('info', text)


    def _sendEvent(self, _type: WorkerEventTypes, serviceId: Optional[str]=None, context: Optional[list[Any]]=None) -> None:
        """
            Send events, which will be process by events' processor.
            Format: WorkerEventTypes, [... data ...]
        """

        try:
            # ALERT! Can raise queue.Full!!!
            self._eventsPipe.put_nowait(
                WorkerEvent( workerId=self._id, type=_type, serviceId=serviceId, context=context )
            )
        except (BrokenPipeError, OSError) as error: pass


    def _del(self) -> None:
        """
            Worker destructor. Use via kill calls and BrokenPipe errors.
        """

        # kill worker and all services
        for service in list(self._services.values()):
            self._killService(service)
        self._sendLog('debug','All services killed.')

        try:
            self._controlPipe.send((WorkerStatus.OK_STATUS, []))
            # waiting for send finish
            time.sleep(self._iteratorDelay * 10)
            self._controlPipe.close()
            self._sendLog('debug', 'Pipe closed.')
        except (BrokenPipeError, OSError) as error:
            self._sendLog('debug', f'Cannot close pipe. {error}')

        # stop iterator
        self._isAlive = False

        self._sendLog('info', 'Worker deleted!')
        # terminate worker process, if its in worker process
        if multiprocessing.current_process() \
            .name.startswith(self.workerPrefix): os._exit(0)


    def _callProcessor(self, name: str, *args) -> None:
        """
            Results:
                ['done', []] - successful command
                ['name', [data]] - successful sent data (reply for the command)
                ['error', ['... description...']] - error message
        """

        self._sendLog('debug', f'System call {name}. Arguments count: {len(args)}')

        # "public" information
        processServices = list(self._services.keys())

        match name:
            case WorkerCall.WORKER_STOP: self._del()
            case WorkerCall.SERVICE_ADD:
                for service in args:
                    if isinstance(service, IService) and service.id not in processServices:
                        # adding service
                        self._addService(service)

                self._sendToPipe((WorkerStatus.OK_STATUS, []))

            case WorkerCall.SERVICE_REMOVE:
                serviceId = args[0]
                if not isinstance(serviceId, str) or serviceId not in processServices:
                    return self._sendToPipe((WorkerStatus.ERROR_STATUS, ['Cannot remove service ', serviceId]))

                self._killService(self._services[serviceId])
                self._sendToPipe((WorkerStatus.OK_STATUS, []))

            case WorkerCall.SERVICES_COUNT:
                self._sendToPipe((WorkerCall.SERVICES_COUNT, [len(self._services)]))

            case WorkerCall.SERVICES:
                self._sendToPipe((WorkerCall.SERVICES, list(self._services.keys())))

            case WorkerCall.SERVICE_CHECK:
                serviceId = args[0]

                if not isinstance(serviceId, str):
                    return self._sendToPipe(
                        ( WorkerStatus.ERROR_STATUS, ['Cannot find service ', serviceId] )
                    )

                self._sendToPipe((WorkerCall.SERVICE_CHECK, [serviceId in processServices]))

            case WorkerCall.SERVICE_HISTORY:
                serviceId = args[0]
                if not isinstance(serviceId, str):
                    return self._sendToPipe( (WorkerStatus.ERROR_STATUS, ['Cannot find service ', serviceId]) )

                self._sendToPipe( (WorkerCall.SERVICE_HISTORY, self._services[serviceId].history) )

        return None


    def _callsInterrupter(self) -> None:
        """
            Interrupt iterator if any call received.
        """

        try:
            if self._controlPipe.poll(timeout=self._iteratorDelay / 2):
                call: tuple[str, tuple|list] = self._controlPipe.recv()
                self._callProcessor(call[0], *call[1])
        except (BrokenPipeError, OSError, EOFError): self._del()


    def _sendToPipe(self, data: Any) -> None:
        try: self._controlPipe.send(data)
        except (BrokenPipeError, OSError, EOFError): self._del()


    def _killService(self, service: IService) -> None:
        # sending event with all service history
        self._sendEvent(
            WorkerEventTypes.SERVICE_FINISHED, serviceId=service.id,
            context=[h for h in service.history()]
        )

        service.kill()
        self._services.pop(service.id)
        self._sendLog('info', f'Service {service.id} killed.')

    def _addService(self, service: IService) -> None:
        self._services[service.id] = service


    def _iterator(self, ):
        if not self._controlPipe:
            self._sendLog('error', 'Cannot start workers iterator without pipe.')
            raise UnableToDo('Cannot start workers iterator without pipe.')

        # inner functions which needed only in iterator
        def checkIfServiceStarted(service: IService) -> bool:
            return any([service.isStarted, service.isWorking])

        self._sendLog('debug', 'Worker (iterator) started.')
        self._sendEvent(WorkerEventTypes.WORKER_STARTED, context=['Worker started.'])

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
                        self._sendEvent(WorkerEventTypes.SERVICE_STARTED, serviceId=serviceId)
                        self._sendLog('debug', f'Process new task from service {serviceId}.')


    def start(self, controlPipe: Connection, eventsPipe: multiprocessing.Queue, logsPipe: Connection) -> None:
        """
            You need to set pipe from the main process to avoid process isolation problems.
            its new process, isolated, because iterator blocks the process/thread
        """

        self._controlPipe = controlPipe
        self._eventsPipe = eventsPipe
        self._logsPipe = logsPipe

        # creating custom stdout for new started worker
        self._customStdout = WorkerStdout(self._sendCaughtLog)

        self._isAlive = True
        try: self._iterator()
        except:
            self._sendEvent(WorkerEventTypes.WORKER_STOPPED, context=['Worker`s iterator stopped.'])
            self._del()



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

    def __init__(self, max_units: int, eventsProcessorDelay: float=0.05, logsHandlerDelay: float=1):
        # changing process creating method
        self._context = multiprocessing.get_context("fork")
        self._max_units = max_units
        self._eventsProcessorDelay = eventsProcessorDelay
        self._logsHandlerDelay = logsHandlerDelay
        self._isLoaded = False
        self._isAlive = True # DO NOT TOUCH IF YOU DONG KNOW WHAT YOU'RE DOING

        # list with active services and workers which process this service
        # format:  service_id : worker_id
        self._processingServices: dict[str, str] = {}
        # saves all history from the service
        self._serviceHistoryBuffer: dict[str, list[HistoryObject]] = {}

        # workers list, to control workers wia Worker ID and workers calls
        # contains workers pipes, which are used to make workers calls
        self._workersConnections: dict[str, Connection] = {}
        self._workersLogsConnections: dict[str, Connection] = {}
        self._workersEventsQueue: multiprocessing.Queue = multiprocessing.Queue() # faster and safer as raw Pipes
        # started workers, contains already started and working worker's ids
        # use it in post load to wait for all workers
        self._startedWorkers: list[str] = []
        # you need to fill it only once - after workers creation
        self._workersLoadTable: dict[str, int] = {} # table for getting worker`s loading fast and secure

        self._globalGSMLock: threading.Lock = threading.Lock()

        # table with all workers processes
        # use it to save and terminate processes
        self._workersProcesses: dict[str, multiprocessing.Process] = {}
        logger.debug('Initialized GlobalServiceManager.')



    @property
    def isLoaded(self) -> bool: return self._isLoaded

    @property
    @afterLoad
    def workersCount(self) -> int: return len(self._workersConnections)

    @property
    @afterLoad
    def processingServices(self) -> list[str]: return list(self._processingServices.keys())

    @property
    @afterLoad
    def servicesCount(self) -> int: return len(self.processingServices)


    @afterLoad
    def _workerCall(self, _id: str, call: str, *args: Any) -> Optional[tuple[int, list[Any]]]:
        connection = self._workersConnections.get(_id)
        if not connection: raise NotFoundException('Connection not found.')
        if call not in WorkerCall._value2member_map_: raise NotFoundException('Call name not found.')

        try:
            connection.send((call, args))

            # receiving data
            if not connection.poll(timeout=5):
                logger.warning(f'Worker {_id} did not respond to {call} within 1s')
                raise BrokenPipeError
            fb, data = connection.recv()

            if fb == WorkerStatus.OK_STATUS:
                logger.debug(f'Successfully worker call. ID: {_id}, Call: {call}, Args count: {len(args)}.')
                return fb, data
        except (BrokenPipeError, OSError, EOFError, ValueError) as error:
            logger.error(f'{_id} did not respond to {call} - finished with error: {error}')
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


    def _processEvent(self, event: WorkerEvent) -> None:
        """
            Only fresh information from the workers.
            Change critically tables only here by workers events.
            This function must be fast as hell.
        """

        with self._globalGSMLock:
            match event.type:
                case WorkerEventTypes.WORKER_STOPPED:
                    process = self._workersProcesses.pop(event.workerId, None)
                    if process: process.terminate()
                case WorkerEventTypes.WORKER_STARTED:
                    self._startedWorkers.append(event.workerId)
                    # adding to the loading table
                    self._workersLoadTable[event.workerId] = 0
                case WorkerEventTypes.SERVICE_STARTED:
                    self._processingServices[event.serviceId] = event.workerId
                case WorkerEventTypes.SERVICE_FINISHED:
                    # also saving service history in buffer
                    self._serviceHistoryBuffer[event.serviceId] = event.context
                    self._processingServices.pop(event.serviceId, None)
                    # and removing it from the load table
                    self._workersLoadTable[event.workerId] -= 1 if self._workersLoadTable[event.workerId] > 0 else 0


    @afterLoad
    def _eventsProcessor(self) -> None:
        """
            Catch and process every worker`s event.
        """

        while self._isAlive:
            try:
                self._processEvent(
                    self._workersEventsQueue.get(timeout=self._eventsProcessorDelay)
                )
            except Empty: continue
            except (BrokenPipeError, OSError, EOFError) as e:
                logger.error(f'Events processor crushed with {e}.')
                break



    @afterLoad
    def _getLessLoadedWorker(self) -> str:
        """
            Get count of processing tasks/services from every worker.
            And then return id of the less loaded worker.
            Returns ID of the worker.
        """

        if len(self._workersLoadTable.keys()) < 1:
            logger.error('No alive workers found in the load table. Cannot get less loaded worker.')
            raise NotFoundException('No alive workers found in the load table.')

        return min(self._workersLoadTable, key=self._workersLoadTable.get)


    @afterLoad
    def _loadService(self, service: IService) -> bool:
        with self._globalGSMLock:
            workerId = self._getLessLoadedWorker()
            self._workersLoadTable[workerId] += 1

        logger.debug(f'Adding new service to {workerId}...')
        result: Optional[tuple[str, Any]] = self._workerCall(workerId, WorkerCall.SERVICE_ADD, service)
        logger.debug(f'Adding to {workerId} - {result}.')

        if result is None or result[0] != WorkerStatus.OK_STATUS:
            with self._globalGSMLock:
                self._workersLoadTable[workerId] -= 1 if self._workersLoadTable[workerId] > 0 else 0
            return False

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
    def remove(self, *args) -> None:
        """
            Analog to the "kill" or terminate service command.
            Use it to terminate service`s task and stop the service.
            (Removes it from the worker)
        """
        results: list[str] = []

        for service in args:
            # if service is not processing now
            if not service.id in self._processingServices: continue

            response = self._workerCall(
                self._processingServices.get(service.id), WorkerCall.SERVICE_REMOVE, service.id
            )
            if not response is None: results.append(service.id)

        logger.info(
            f'Successfully removed (stopped) { len(list(filter(lambda x: x, results))) } services.',
            ' [' + ' ,'.join(results) + ']' if results else ''
        )

    def getServiceHistory(self, service: IService) -> Optional[list[HistoryObject]]:
        # getting worker which process this service
        return self._serviceHistoryBuffer.pop(service.id, None)


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

            # new connection for logs
            logsParentPipe, logsChildPipe = multiprocessing.Pipe()
            self._workersLogsConnections[worker.id] = logsParentPipe

            # DO NOT USE DAEMON PROCESSES WITH FORK CONTEXT - YOU CANNOT USE ASYNC WITH THEM
            workerProcess = self._context.Process(
                target=worker.start,
                args=(controlChildPipe, self._workersEventsQueue, logsChildPipe),
                name=f"{worker.workerPrefix}_{worker.id}"
            )
            self._workersProcesses[worker.id] = workerProcess
            workerProcess.start()
            logger.debug(f'Starting worker {worker.id}...')


        logger.info('Global service manager started.')
        self._isLoaded = True

        # post loading
        logger.debug(f'Starting logs handler.')
        threading.Thread(target=self._logsHandler, daemon=True, name="GSM-LogsHandler").start()
        logger.debug(f'Starting events processor.')
        threading.Thread(target=self._eventsProcessor, daemon=True, name="GSM-EventProcessor").start()

        # waiting for all workers to avoid "pipe has not been loaded yet" problems
        # and to don't lose data (like services which you need to add)
        logger.debug(f'Waiting for {len(self._workersProcesses.keys())} workers to start.')
        while len(self._workersProcesses.keys()) != len(self._startedWorkers):
            time.sleep(self._logsHandlerDelay)


    @afterLoad
    def kill(self) -> bool:
        """
            Hard kill the workers. Terminate all processes.
            Use it only in "hard" situation.
        """
        with self._globalGSMLock:
            logger.debug(f'Terminating (hard kill) all workers ({len(self._workersProcesses)})...')
            for process in list(self._workersProcesses.values()):
                process.terminate()

            logger.debug(f'Killed all workers - {len(self._workersConnections)} units. Closing GSM.')
            self._isAlive = False
            self._isLoaded = False

        return True
