from meta.queue import IQueue
from core.tasks.task import Task


class TaskQueue(IQueue):
    def __init__(self):
        self._tasks = []

    def start(self) -> bool: ...

    def add(self, task: Task) -> None:
        self._tasks.append(task)

    def get(self) -> Task:
        return self._tasks.pop(0)

    def makeEmpty(self): self._tasks.clear()

    @property
    def size(self) -> int:
        return len(self._tasks)