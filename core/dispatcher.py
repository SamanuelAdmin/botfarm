import time
from dataclasses import dataclass
from datetime import datetime

from core.core import Core
from core.middleware import afterLoad
from services.panel_manager.manager import PanelManager
from scripts.control_script import *


logger = Logger()

@dataclass
class ActiveAccount:
    accountUsername: str
    serviceId: str


class Dispatcher:
    """
        Main manager for moderate orders, process it and manage accounts.
        New abstract layer for the system.
        Active accounts - accounts, which we can already use
        (which are connected to the phone and are workable)

        TODO: make a system for handling active accounts and using it for the orders.
        Scheme:
        While loading - collect all active accounts from all available services (just get all usernames from accounts list).
        Then add it to the active-accounts table (format account_username -> ActiveAccount obj)
        And use if for orders
    """

    def __init__(self, core: Core,  panelManager: PanelManager):
        self._core = core
        self._panelManager = panelManager

        self._isLoaded = False
        self.activeAccounts: dict[str, ActiveAccount] = {}


    @property
    def isLoaded(self) -> bool: return self._isLoaded


    @afterLoad
    def update(self):
        """
            Update function for orders.
            Getting new orders via manager.
        """

        newOrders = self._panelManager.getNewOrders()


    def load(self):
        """
            Function for starting all loading processes.
            Getting all active accounts using adbScript for parsing them all.
        """
        logger.info('loading dispatcher...')
        startTime = datetime.now()

        for serviceId in self._core.servicesTable:
            self._core.addTaskToService(serviceId, parseActiveAccounts)
            self._core.processService(serviceId)

            while True:
                print(self._core.getServiceHistory(serviceId))
                time.sleep(1)

            break


        self._isLoaded = True
        logger.info(f'Dispatcher loaded in {(datetime.now() - startTime).total_seconds()} seconds.')




