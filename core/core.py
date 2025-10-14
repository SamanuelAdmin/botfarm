from datetime import datetime
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any

from core.core_configurator import CoreConfigurator
from core.logger import Logger, Log
from core.service import IService, Service
from core.exceptions import *
from core.global_service_queue import GlobalServiceManager
from core.tasks.task import ITask, Task
from core.middleware import *
from meta import singleton
from meta.singleton import Singleton
from services.adb_manager import AdbClient, AdbManager
from services.adb_manager.adb_auto import AdbAutomatization
from services.adb_manager.exceptions import IncorrectStatusCodeException
from services.db_services import accounts_manager, adb_hub_manager


class ICore(ABC):
    __metaclass__ = singleton.Singleton

    @abstractmethod
    def load(self) -> bool: ...

    @abstractmethod
    def start(self) -> bool: ...



class Core(ICore):
    """
        System to control all devices at the same time.
        Also control database via services.

        Creating database services - config section (config method)
        Loading hubs

        service is the obj that can control device and modules,
        which are used to control device
        map of the service table:
        key: device_serial@hub_uuid
        value: IService`s class obj

        Hub table - table with all hubs controllers (AdbManagers)
        mapping for all adb hubs (adb managers)
        (key) hub_uuid : AdbManager
    """

    __metaclass__ = Singleton


    def __init__(self, logger: Optional[Logger]=None):
        # gotten from loader (all private)
        self.__logger = logger

        # tables
        self._services: dict[str, IService] = {}
        self._hubs: dict[str, AdbManager] = {}

        self._configurator: CoreConfigurator
        self._GSQ: GlobalServiceManager
        # DB services
        self._adbHubManager: adb_hub_manager.AdbHubManager
        self._accountsManager: accounts_manager.AccountsManager

        # core flags
        self.__isInitialized: bool = False
        self.__isConfigured: bool = False
        self._isStarted: bool = False

    @property
    def ready(self):
        """
            True if core is loaded and started.
        """
        return self.__isInitialized and self.__isConfigured


    def _logAction(self, _type: str, *info):
        self.__logger.add(
            Log(_type, *info, setDatetime=True)
        )

    def _createServices(self, hubUUID: str) -> int:
        adbHubManager = self._hubs.get(hubUUID)
        if not adbHubManager:
            self._logAction('error', f'Cannot find adb hub in HUB TABLE by UUID: {hubUUID}.')
            raise AdbManagerNotFound(f'Cannot find AdbManager (adb hub) #{hubUUID} in HUBD TABLE.')

        adbHubManager.loadAllSerials()
        self._logAction('info', f'{hubUUID} Loaded all adb clients. Creating services...')

        allLoadedClients: dict[str, AdbClient] = adbHubManager.getAllLoadedSerials()

        for serial, adbClient in allLoadedClients.items():
            serviceId = f'{serial}@{hubUUID}'

            # adding adb API to service
            newService = Service(
                _id=serviceId, adbClient=adbClient
            )

            self._services[serviceId] = newService

        newServicesCount = len(allLoadedClients.keys())
        self._logAction('info', f'{hubUUID} Loaded all ({newServicesCount}) adb clients.')

        return newServicesCount


    def loadAdbHub(self, adbManager: AdbManager) -> bool:
        try:
            hubUUID = adbManager.getUUID()

            # if hub has no UUID - skip it
            if hubUUID is None:
                raise IncorrectStatusCodeException(404, adbManager.api)
        except IncorrectStatusCodeException:
            self._logAction('error', f'Cannot get UUID of adb hub. Skipped.')
            return False


        self._hubs[hubUUID] = adbManager

        # loading hub
        self._hubs[hubUUID].loadAllSerials()
        self._createServices(hubUUID)
        self._logAction('info', f'Loaded new hub with UUID: {hubUUID}.')

        return True


    def configure(self, configurator: CoreConfigurator) -> None:
        """
            all configs for the core
            accept only in CoreConfigurator format (dataclass)
        """
        self._configurator = configurator
        self.__isConfigured = True


    def load(self) -> bool:
        if not self.__isConfigured:
            raise CoreIsNotConfigured()

        # objs for db connections
        self._adbHubManager = adb_hub_manager.AdbHubManager()
        self._accountsManager = accounts_manager.AccountsManager()

        loadStartTime = datetime.now()
        self._logAction('info', 'Start loading...')

        # fill out HUBS TABLE and SERVICES TABLE
        for adbHubRecord in self._adbHubManager.getAll():
            adbManager = AdbManager(adbHubRecord.apiLink, timeout=self._configurator.hub_response_timeout)

            if not self.loadAdbHub(adbManager):
                continue # skip this hub

        self._GSM = GlobalServiceManager(self._configurator.max_gsq_units)
        self._GSM.load()
        self._logAction('info', f'Created and started {self._GSM.workersCount} workers.')
        self._logAction('info', f'Global service manager loaded. Loading services to GSM...')

        self.__isInitialized = True
        loadTime = (datetime.now() - loadStartTime).total_seconds()
        self._logAction('info', f'Load finished in {loadTime}s.')
        return True


    def start(self) -> bool:
        if not self.__isInitialized:
            raise CoreIsNotInitialized()

        self._logAction('info', 'Core started.')
        self._isStarted = True
        return True


    def stop(self):
        self._GSM.kill()

        self._isStarted = False
        self._logAction('info', 'Core stopped.')


    @syscall
    def addTaskToService(self, service: IService|str, function: ADB_SCRIPT_CONTRACT, *args, **kwargs) -> bool:
        """
            Syscall for adding a task to the service by its ID.
            Create task using function, args and kwargs.
            Do not set AdbClient and AdbAuto to the args ot kwargs.
            These will be deleted automatically.
        """

        task: ITask = Task(
            function,
            service.inner.get('adbClient'), service.inner.get('adbAuto'),
            *args, **kwargs
        )

        # check if service`s id is correct
        addingResult = bool(service.loadTask(task)) # now we have loaded service
        self._logAction('info', f'Adding new task to service {service}. Success - {addingResult}.')

        # adding to the GSM to process task
        self._GSM.add(service)
        return addingResult
