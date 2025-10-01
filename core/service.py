import asyncio
import time
from abc import ABC, abstractmethod, abstractproperty
from typing import Callable, Any, List, Optional

from core.tasks.queue import TaskQueue
from core.tasks.task import Task, ITask
from services.adb_manager import AdbClient
from services.adb_manager.adb_auto import AdbAutomatization


class IService(ABC):
    _id: str
    _taskQueue: TaskQueue

    @abstractmethod
    def __init__(self, _id: str): ...

    @property
    @abstractmethod
    def id(self) -> str: ...

    @property
    @abstractmethod
    def loadedTasksCount(self) -> int: ...

    @property
    @abstractmethod
    def isWorking(self) -> bool: ...

    @property
    @abstractmethod
    def loadTask(self) -> int: ...

    @abstractmethod
    async def start(self) -> bool: ...
    @abstractmethod
    def wait(self) -> bool: ...
    @abstractmethod
    def kill(self) -> bool: ...


class TaskHistory:
    def __init__(self):
        self._history: List[tuple[str, bool | Exception]] = []

    def find(self, taskId: str) -> Optional[bool | Exception]:
        for line in self._history:
            if line[0] == taskId:
                return line[1]

        return None

    def add(self, taskId: str, result: bool | Exception) -> None:
        self._history.append((taskId, result))

    @property
    def history(self) -> List[tuple[str, bool | Exception]]:
        return self._history



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

    def __del__(self):
        self.kill()


    @property
    def id(self): return self._id

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
    def isBlocked(self):
        return self._blocker

    def deleteAllTasks(self) -> bool:
        self._taskQueue.makeEmpty()
        return True

    def loadTask(self, task: ITask) -> int:
        '''
            Process task, adding service`s adb api (adbClient)
            and add task to queue.
            Returns loaded tasks cound.
        '''
        self._taskQueue.add(task)
        return self.loadedTasksCount


    def _iterator(self):
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
            self._taskHistory.add(task.taskId, taskResult)
            self._isWorking = False

            if self._singleTaskMode:
                # block after every task
                self._blocker = True


    async def start(self) -> bool:
        # start via asyncio.run() or create_task
        # will block a thread!!! if yuu use await or run
        self._blocker = False
        await asyncio.to_thread(self._iterator)
        return True

    def wait(self):
        self._blocker = True

    def kill(self):
        self._isWorking = False
        self._blocker = True
        self._taskQueue.makeEmpty()
        self._isAlive = False
