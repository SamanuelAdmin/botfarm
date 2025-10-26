import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import dataclass
from datetime import datetime

from core.core import Core
from core.middleware import afterLoad
from core.service import HistoryObject
from services.panel_manager.manager import PanelManager
from scripts.control_script import *
from scripts.selling_services_scripts import *
from services.panel_manager.models import OrderData

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


    def _loadService(self, serviceId: str) -> list[str]:
        """
            Post load for a service.
            Getting all active accounts via syscalls and adbScript.
        """

        self._core.addTaskToService(serviceId, parseActiveAccounts)
        self._core.processService(serviceId)
        data: Optional[list[HistoryObject]]

        while True:
            data = self._core.getServiceHistory(serviceId)
            if data: break

        for username in data[0].result:
            self.activeAccounts[username] = ActiveAccount(username, serviceId)

        return data[0].result


    def load(self):
        """
            Function for starting all loading processes.
            Getting all active accounts using adbScript for parsing them all.
        """

        logger.info('loading dispatcher...')
        startTime = datetime.now()

        threads = [
            threading.Thread(target=self._loadService, args=(serviceId, )) \
            for serviceId in self._core.servicesTable
        ]

        logger.info('Starting all threads to process services...')
        for thread in threads: thread.start()
        time.sleep(5) # small delay to start all threads
        for thread in threads: thread.join()

        self._isLoaded = True
        logger.info(f'Collected {len(self.activeAccounts)} (active) accounts.')
        logger.info(f'Dispatcher loaded in {(datetime.now() - startTime).total_seconds()} seconds.')


    @afterLoad
    def processOrder(self, order: OrderData):
        if order.quantity != 34: return

        # making tasks for services



    def handler(self):
        while True:
            for order in self._panelManager.getNewOrders():
                # making tasks
                pass