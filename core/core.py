from datetime import datetime
from abc import ABC, abstractmethod
from typing import Optional

from core.core_configurator import CoreConfigurator
from core.logger import Logger, Log
from core.service import IService, Service
from core.exceptions import AdbManagerNotFound, CoreIsNotInitialized
from meta import singleton
from meta.singleton import Singleton
from services.adb_manager import AdbClient, AdbManager


class ICore(ABC):
    __metaclass__ = singleton.Singleton

    @abstractmethod
    def load(self) -> bool: ...

    @abstractmethod
    def start(self) -> bool: ...



class Core(ICore, metaclass=Singleton):

    def __init__(self, adbHubs: list[AdbManager], logger: Optional[Logger]=None):
        '''
            service is the obj that can control device and modules,
            which are used to control device
            map of the service table:
            key: device_serial@hub_uuid
            value: IService`s class obj

            Hub table - table with all hubs controllers (AdbManagers)
            mapping for all adb hubs (adb managers)
            (key) hub_uuid : AdbManager
        '''

        # gotten from loader (all private)
        self.__adbHubs: list[AdbManager] = adbHubs
        self.__logger = logger

        # tables
        self._services: dict[str, IService] = {}
        self._hubs: dict[str, AdbManager] = {}

        # core flags
        self.__isInitialized: bool = False
        self.__isConfigured: bool = False


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
            newService = Service(_id=serviceId)

            self._services[serviceId] = newService

        newServicesCount = len(allLoadedClients.keys())
        self._logAction('info', f'{hubUUID} Loaded all ({newServicesCount}) adb clients.')

        return newServicesCount


    def _loadAdbHub(self, adbManager: AdbManager) -> bool:
        hubUUID = adbManager.getUUID()
        # if hub has no UUID - skip it
        if hubUUID is None:
            self._logAction('error', f'Cannot get UUID of adb hub. Skipped.')
            return False

        self._hubs[hubUUID] = adbManager

        # loading hub
        self._hubs[hubUUID].loadAllSerials()
        self._createServices(hubUUID)
        self._logAction('info', f'Loaded new hub with UUID: {hubUUID}.')

        return True


    def configure(self, configurator: CoreConfigurator):
        # here will be all core configs
        pass


    def load(self) -> bool:
        loadStartTime = datetime.now()
        self._logAction('info', 'Start loading...')

        # fill out HUBS TABLE and SERVICES TABLE
        for adbManager in self.__adbHubs:
            if not self._loadAdbHub(adbManager):
                # here will be a warning
                continue

        self.__isInitialized = True
        loadTime = (datetime.now() - loadStartTime).total_seconds()
        self._logAction('info', f'Load finished in {loadTime}s.')
        return True


    def start(self) -> bool:
        if not self.__isInitialized:
            raise CoreIsNotInitialized()

        return True