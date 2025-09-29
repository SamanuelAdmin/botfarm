from tasks.task import ITask


class TaskError(Exception):
    def __init__(self, task: ITask):
        self.task = task

class NotFoundException(Exception):
    def __init__(self, info: str):
        self.info = info

    def __str__(self): return self.info


class TaskAlreadyStarted(TaskError):
    def __init__(self, task: ITask):
        super().__init__(task)

    def __str__(self): return f'Task #{self.task.taskId} already started.'


class TaskNotStarted(TaskError):
    def __init__(self, task: ITask):
        super().__init__(task)

    def __str__(self): return f'Task #{self.task.taskId} is not started.'


class AdbManagerNotFound(Exception):
    def __init__(self, info: str):
        super().__init__(info)


class CoreIsNotInitialized(Exception):
    def __str__(self): return 'Core not initialized. Run .load method before starting.'


class UnableToDo(Exception):
    def __init__(self, info: str):
        super().__init__(info)