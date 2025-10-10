import multiprocessing
import queue
from abc import ABC, abstractmethod
import time
from typing import Callable, Any, Optional
import uuid

from core.exceptions import TaskAlreadyStarted, TaskNotStarted
from core.middleware import ADB_SCRIPT_CONTRACT
from services.adb_manager import AdbClient
from services.adb_manager.adb_auto import AdbAutomatization


class ITask(ABC):
    _id: str
    _function: Callable
    _functionArgs: tuple
    _functionKwargs: dict

    @abstractmethod
    def start(self) -> bool: ...
    @abstractmethod
    def stop(self) -> bool: ...

    @property
    @abstractmethod
    def taskId(self) -> str: ...



class Task(ITask):
    _function: ADB_SCRIPT_CONTRACT

    def __init__(
            self, function: ADB_SCRIPT_CONTRACT,
            adbClient: AdbClient, adbAuto: AdbAutomatization,
            *functionArgs, **functionKwargs ):
        self._id: str = str(uuid.uuid4())

        self._function = function
        self._functionArgs = (adbClient, adbAuto, *functionArgs)
        self._functionKwargs = functionKwargs

        self._task: Optional[multiprocessing.Process] = None
        self._dataQueue: multiprocessing.Queue
        self._taskResult: Optional[Any] = None

        self._isFinished: bool = False
        self._checkerDelay: float = 0.05


    @property
    def taskId(self) -> str:
        return self._id


    def start(self) -> bool | Exception:
        """
            Can be unoptimized as fuck because of new process for every task.
            Remove this shit if system is too heavy
        """

        if self._task: raise TaskAlreadyStarted(self)
        self._dataQueue = multiprocessing.Queue()

        def taskBody(task: ITask, queue: multiprocessing.Queue) -> None:
            try:
                taskResult = task._function(
                    *task._functionArgs, **task._functionKwargs
                )

                queue.put(taskResult)
            except Exception as error:
                queue.put(error)


        self._task = multiprocessing.Process(target=taskBody, args=(self, self._dataQueue), daemon=True)
        self._task.start()

        # self._task.join() DO NOT USE JOIN, it will block all main process
        # USE CHECKER INSTEAD
        while True:
            try:
                self._taskResult = self._dataQueue.get()
                return self._taskResult
            except queue.Empty:
                time.sleep(self._checkerDelay)



    def stop(self) -> None:
        if not self._task: raise TaskNotStarted(self)

        self._task.terminate()
