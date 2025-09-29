import threading
from abc import ABC, abstractmethod, abstractproperty
from typing import Callable, Any, List, Optional

from core.tasks.queue import TaskQueue
from core.tasks.task import Task


class IService(ABC):
    _id: str
    _taskQueue: TaskQueue

    @abstractmethod
    def __init__(self, _id: str): ...

    @abstractmethod
    def start(self) -> bool: ...
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


    def __init__(self, _id, singleTaskMode: bool=True):
        self._id = _id
        self._taskQueue = TaskQueue()

        # MODES
        # process only one task - then block iterator
        # use with global services queue
        self._singleTaskMode = singleTaskMode

        # block iterator when task already started
        # 1 service = 1 task at the moment
        self._blocker = threading.Event()
        self._iterator = threading.Thread(target=self._iteratorBody, daemon=True)
        self._taskHistory: TaskHistory = TaskHistory()
        self._isWorking = False

    def __del__(self):
        self.kill()

    @property
    def getCurrentTask(self) -> Task:
        return self._currentTask

    @property
    def loadedTasksCount(self) -> int:
        return self._taskQueue.size

    @property
    def isWorking(self) -> bool:
        return self._isWorking

    @property
    def isBlocked(self):
        return not self._blocker.is_set()


    def deleteAllTasks(self) -> bool:
        self._taskQueue.makeEmpty()

    def loadTask(self, task: Task) -> int:
        # returns loaded task size
        self._taskQueue.add(task)
        return self.loadedTasksCount


    def _iteratorBody(self):
        while True:
            self._blocker.wait()
            if self._taskQueue.size == 0: continue

            # getting new task
            task = self._taskQueue.get()
            self._currentTask = task

            self._isWorking = True
            taskResult = task.start()
            self._taskHistory.add(task.taskId, taskResult)
            self._isWorking = False

            if self._oneTaskMode: self.wait()


    def start(self) -> bool:
        self._blocker.set()
        return True

    def wait(self):
        self._blocker.wait()

    def kill(self):
        pass