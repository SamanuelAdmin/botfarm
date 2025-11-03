import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional

from core.tasks.queue import TaskQueue
from core.tasks.task import ITask
from core.hardware import AdbClient
from core.hardware.adb_auto import AdbAutomatization



class IService(ABC):
    """
        isStarted - if iterator has been started
        isWorking - if service is processing a script
    """

    _id: str
    _taskQueue: TaskQueue

    @abstractmethod
    def __init__(self, _id: str): ...

    @property
    @abstractmethod
    def id(self) -> str: ...

    @abstractmethod
    def history(self, *args, **kwargs) -> list: ...

    @property
    @abstractmethod
    def inner(self) -> dict[str, Any]: ...

    @property
    @abstractmethod
    def loadedTasksCount(self) -> int: ...

    @property
    @abstractmethod
    def isWorking(self) -> bool: ...

    @property
    @abstractmethod
    def isStarted(self) -> bool: ...

    @abstractmethod
    def loadTask(self, task: ITask) -> int: ...

    @abstractmethod
    def deleteAllTasks(self) -> None: ...

    @abstractmethod
    def start(self) -> bool: ...
    @abstractmethod
    def wait(self) -> bool: ...
    @abstractmethod
    def kill(self) -> bool: ...



@dataclass
class HistoryObject:
    taskId: str
    result: Any
    def __str__(self): return f'{self.taskId}: {self.result}'

class TaskHistory:
    def __init__(self):
        # format: taskId -> HistoryObject
        self._history: dict[str, HistoryObject] = {}

    def get(self, taskId: str) -> Optional[Any]:
        return self._history.pop(taskId, None)

    def add(self, historyObject: HistoryObject) -> None:
        self._history[historyObject.taskId] = historyObject

    def getAll(self) -> List[HistoryObject]:
        """
            Get all history records and clear it.
        """

        result = []

        for key in list(self._history.keys()):
            result.append(self._history[key])
            del self._history[key]

        return result

    @property
    def size(self) -> int: return len(self._history)


class Service(IService):
    _id: str
    _taskQueue: TaskQueue

    def __init__(self, _id: str, adbClient: AdbClient, singleTaskMode: bool=True, iteratorDelay: float=0.05):
        self._id = _id
        self._taskQueue = TaskQueue()

        # ADB API
        self._adbClient = adbClient
        self._adbAuto = AdbAutomatization(self._adbClient)

        # MODES
        # process only one task - then block iterator
        # use with global services queue
        self._singleTaskMode = singleTaskMode
        self._iteratorDelay = iteratorDelay

        self._taskHistory: TaskHistory = TaskHistory()
        self._currentTask: Optional[ITask] = None

        # CONTROL FLAGS
        # block iterator when task already started
        # 1 service = 1 task at the moment
        self._blocker: bool = False # block = True, False is unblocked
        self._isWorking = False
        self._isAlive: bool = True # kill iterator when its false
        self._isIteratorStarted: bool = False

    def __del__(self):
        self.kill()

    def __str__(self):
        return f'service_{self._id}'

    @property
    def id(self): return self._id

    @property
    def inner(self) -> dict[str, Any]:
        """
            Returns all inner objects, which you need to use as an API.
            For example AdbClient and AdbService for tasks creations
        """
        return {
            'adbClient': self._adbClient,
            'adbAuto': self._adbAuto
        }

    def history(self, taskId: Optional[str]=None) -> list[HistoryObject]:
        if taskId: return [self._taskHistory.get(taskId)]
        return self._taskHistory.getAll()

    @property
    def getCurrentTask(self) -> ITask:
        return self._currentTask

    @property
    def loadedTasksCount(self) -> int:
        return self._taskQueue.size

    @property
    def isWorking(self) -> bool:
        return self._isWorking

    @property
    def isStarted(self) -> bool:
        return self._isIteratorStarted

    @property
    def isBlocked(self):
        return self._blocker

    def deleteAllTasks(self) -> bool:
        self._taskQueue.makeEmpty()
        return True

    def loadTask(self, task: ITask) -> int:
        '''
            Process task, adding service`s hardware api (adbClient)
            and add task to queue.
            Returns loaded tasks cound.
        '''
        self._taskQueue.add(task)
        return self.loadedTasksCount


    def _iterator(self):
        self._isIteratorStarted = True

        while True:
            # iterator killer
            if not self._isAlive: break

            if self._blocker or self._taskQueue.size == 0:
                time.sleep(0.05)
                continue

            # getting new task
            task = self._taskQueue.get()
            self._currentTask = task

            self._isWorking = True
            # must block all code func (IO bound)
            taskResult = task.start()
            self._isWorking = False
            self._taskHistory.add(
                HistoryObject(taskId=task.taskId, result=taskResult)
            )

            if self._singleTaskMode:
                # block after every task AND EXIT ITERATOR! 1 start = 1 task
                self._blocker = True
                break

        self._isIteratorStarted = False


    def start(self) -> bool:
        # DO NOT USE ASYNCIO! Use threads instead
        self._blocker = False

        if not self._isIteratorStarted:
            threading.Thread(target=self._iterator).start()
            self._isAlive = True

        return True

    def wait(self):
        self._blocker = True

    def kill(self):
        self._isWorking = False
        self._blocker = True
        self._isIteratorStarted = False
        self._taskQueue.makeEmpty()
        self._isAlive = False

        if self._currentTask:
            self._currentTask.stop()
