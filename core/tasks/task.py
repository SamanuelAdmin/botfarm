import threading
from abc import ABC, abstractmethod, abstractproperty
from typing import Callable, Any, Optional
import uuid

from core.exceptions import TaskAlreadyStarted, TaskNotStarted



class ITask(ABC):
    _function: Callable


    @abstractmethod
    def start(self) -> bool: ...
    @abstractmethod
    def stop(self) -> bool: ...

    @abstractproperty
    def taskId(self) -> int: ...



class Task(ITask):
    _function: Callable[[Any], Any]

    def __init__(self, function: Callable[[Any], Any], *functionArgs, **functionKwargs):
        self._id: str = str(uuid.uuid4())

        self._function = function
        self._functionArgs = functionArgs
        self._functionKwargs = functionKwargs

        self.task: Optional[threading.Thread] = None
        self.taskResult: Optional[Any] = None


    @property
    def taskId(self) -> str:
        return self._id


    def start(self) -> bool | Exception:
        if self.task: return TaskAlreadyStarted(self)

        def taskBody(self: Task):
            self.taskResult = None

            try:
                self.taskResult = self._function(
                    *self._functionArgs, **self._functionKwargs
                )
            except Exception as error:
                self.taskResult = error


        self.task = threading.Thread(target=taskBody, args=(self, ))
        self.task.start()
        self.task.join()

        return self.taskResult



    def stop(self) -> bool | Exception:
        # if not self.task: return TaskNotStarted(self)
        # !TODO FINISH THIS SHIT
        pass
