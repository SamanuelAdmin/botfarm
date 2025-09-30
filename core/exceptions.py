class TaskError(Exception):
    def __init__(self, task):
        self.task = task

class NotFoundException(Exception):
    def __init__(self, info: str):
        self.info = info

    def __str__(self): return self.info


class TaskAlreadyStarted(TaskError):
    def __str__(self):
        return f'Task #{self.task.taskId} already started.'


class TaskNotStarted(TaskError):
    def __str__(self):
        return f'Task #{self.task.taskId} is not started.'


class AdbManagerNotFound(Exception):
    def __init__(self, info: str):
        super().__init__(info)


class CoreIsNotInitialized(Exception):
    def __str__(self): return 'Core is not initialized. Run .load method before starting.'

class CoreIsNotConfigured(Exception):
    def __str__(self): return 'Core is not configured. Run .configure method before starting.'


class UnableToDo(Exception):
    def __init__(self, info: str):
        super().__init__(info)


class IncorrectConfigsFormat(Exception):
    def __str__(self): return 'Incorrect configs format. JSON format only!'


class ServiceAlreadyInWork(Exception): pass