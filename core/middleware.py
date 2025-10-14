"""
    DECORATORS AND MIDDLEWARE (LOGIC)
"""
import copy
from functools import wraps
from typing import Callable, Any

from core.exceptions import NotFoundException, CoreIsNotStarted, NotLoaded
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

        # checking if core is started
        if not core.ready:
            raise CoreIsNotStarted()

        # core - self, core obj
        # check is service is exists
        service = core._services.get(serviceId)
        if not service: raise NotFoundException(f'Service {serviceId} not found.')

        return function(core,  service, *args, **kwargs)

    return wrapper


def afterLoad(function: Callable) -> Callable:
    """
        Decorator, which can guarantee that object has been loaded.
        Use isLoaded property to check if object has been loaded.

        Usage:
            @afterLoad
            def action(self, *args, **kwargs) -> Any: ...
    """

    @wraps(function)
    def wrapper(obj, *args, **kwargs) -> Any:
        if not hasattr(obj, 'isLoaded'):
            raise NotFoundException(f'Object {obj} has no required "isLoaded" property.')
        if not obj.isLoaded: raise NotLoaded()

        result = function(obj, *args, **kwargs)
        return result

    return wrapper



ADB_SCRIPT_CONTRACT = Callable[[AdbClient, AdbAutomatization, Any, Any], bool] # annotation for adbScript decorator

def adbScript(function: ADB_SCRIPT_CONTRACT) -> Callable:
    """
        ADB script standard.

        Format of functions:
        def action(adbClient: AdbClient, adbAuto: AdbAutomatization, *args, **kwargs) -> bool: ...

        Where:
        - adbClient: AdbClient - API to system hardware part. Let control phones via ADB and get data
        like screen dumps, screenshots etc. Required.
        - adbAuto: AdbAutomatization - wrapper for adbClient, has automatization functions,
        makes scripts easy-to-read, simpler to write and more compact.
        - args and kwargs: useful information for this script, like logins, text, posts info etc.
    """

    @wraps(function)
    def wrapper(adbClient: AdbClient, adbAuto: AdbAutomatization, *args, **kwargs):
        result = function(
            adbClient, adbAuto, *args, **kwargs
        )
        return result

    return wrapper
