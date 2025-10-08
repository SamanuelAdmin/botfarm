"""
    DECORATORS AND MIDDLEWARE (LOGIC)
"""
import copy
from functools import wraps
from typing import Callable, Any

from core.exceptions import NotFoundException, CoreIsNotStarted
from services.adb_manager import AdbClient
from services.adb_manager.adb_auto import AdbAutomatization



def syscall(function: Callable) -> Callable:
    """
        Syscalls is methods which can control core actions.
        Like "Core API".
        This decorator check if core is loaded and inited, before
        calling system calls.
    """

    @wraps(function)
    def wrapper(core, serviceId: str, *args, **kwargs) -> Any:
        # core - "self" link analog
        # deleting AdbClient and AdbAuto from args
        args = [obj for obj in copy.deepcopy(args) if not isinstance(obj, (AdbClient, AdbAutomatization))]

        # deleting AdbClient and AdbAuto from kwargs
        kwargs = {key: value for key, value in copy.deepcopy(kwargs).items() if not isinstance(value, (AdbClient, AdbAutomatization))}

        # core - self, core obj
        # check is service is exists
        service = core._services.get(serviceId)
        if not service: raise NotFoundException(f'Service {serviceId} not found.')

        if not core.isReady:
            raise CoreIsNotStarted()

        return function(core,  service, *args, **kwargs)

    return wrapper