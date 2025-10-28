import copy
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core.core import Core
from core.middleware import afterLoad, ADB_SCRIPT_CONTRACT
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
    busy: bool = False
    taskId: Optional[str] = None


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

    def __init__(self, core: Core, panelManager: PanelManager, orderProcessorDelay: int=1):
        self._core: Core = core
        self._panelManager: PanelManager = panelManager

        self._orderProcessorDelay: int = orderProcessorDelay
        self._isLoaded: bool = False

        self._crspServiceAccount: dict[str, list[ActiveAccount]] = {} # correspondence table (service_id -> list of active accounts)
        self._globalDispatcherLock = threading.Lock()
        self._processingOrders: list[OrderData] = []
        # services which are processing or which need to give their history (won't be touched be orderProcessor)
        self._blockedServices: list[str] = []

        # all selling scripts will be here in format SERVICE_ID : ADB_SCRIPT
        self._sellingScripts: dict[int, ADB_SCRIPT_CONTRACT] = {
            9216: likePost,
            9217: followAccount
        }


    @property
    def isLoaded(self) -> bool: return self._isLoaded

    @property
    def activeAccountsCount(self) -> int:
        return sum([len(al) for al in self._crspServiceAccount.values()])



    def _freeAccount(self, account: ActiveAccount) -> None:
        with self._globalDispatcherLock:
            account.busy = False
            account.taskId = None


    def _loadService(self, serviceId: str) -> None:
        """
            Post load for a service.
            Getting all active accounts via syscalls and adbScript.
        """

        self._core.addServiceTask(serviceId, parseActiveAccounts)
        self._core.processService(serviceId)
        data: Optional[list[HistoryObject]]

        while True:
            time.sleep(0.1)
            data = self._core.serviceHistory(serviceId)
            if data: break

        if not isinstance(data[0].result, list):
            logger.error(f'Got uncorrected data when getting active account from the service {serviceId}: {data[0].result}')
            return

        self._crspServiceAccount[serviceId] = [
            ActiveAccount(
                accountUsername=username, serviceId=serviceId, busy=False
            ) for username in data[0].result
        ]


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
        time.sleep(self._orderProcessorDelay * 5) # small delay to start all threads
        for thread in threads: thread.join()

        self._isLoaded = True
        logger.info(f'Collected {self.activeAccountsCount} (active) accounts.')
        logger.info(f'Dispatcher loaded in {(datetime.now() - startTime).total_seconds()} seconds.')


    @afterLoad
    def _processOrder(self, order: OrderData, adbFunc: ADB_SCRIPT_CONTRACT, *adbFuncArgs, **adbFuncKwargs) -> bool:
        """
            Makes all order "magic". Added new tasks to free accounts,
            pushing loaded services etc.
            Quantity - count of the "operations"
            adbFunc, adbFuncArgs and adbFuncKwargs - context and algorithm
            which you need to do [Quantity] times.
        """
        totalQuantity = copy.copy(order.quantity)
        with self._globalDispatcherLock:
            self._processingOrders.append(order)

        usedAccounts: list[ActiveAccount] = [] # all successfully processed accounts (all unsuccessful will be removed)
        # to make search actions by task id O(1) using hashmaps
        usedAccountSearcher: dict[str, ActiveAccount] = {} # taskId : ActiveAccount
        # DO NOT DELETE SERVICES FROM THIS LIST
        usedServices: list[str] = [] # services which we used (and don't need to touch anymore)


        def loadServiceTask(serviceId: str, username: str) -> str:
            """ adding tasks and push loaded service to GSM """
            self._core.addServiceTask(serviceId, changeAccount, username)
            return self._core.addServiceTask(serviceId, adbFunc, *adbFuncArgs, **adbFuncKwargs)


        try:
            # looking for free services to complete the order quickly
            # and also collect data from processed services
            while totalQuantity > 0:
                time.sleep(self._orderProcessorDelay)

                # checking for free services
                for serviceId in self._core.servicesTable:
                    with self._globalDispatcherLock:
                        currentCoreLoads: list[str] = self._core.getLoads(serviceId)

                    # ignore if already processing all order
                    if len(usedAccounts) >= order.quantity: break

                    with self._globalDispatcherLock:
                        # skip if service is busy
                        if serviceId in currentCoreLoads: continue
                        if serviceId in self._blockedServices: continue
                        if serviceId in usedServices: continue

                    for account in self._crspServiceAccount[serviceId]:
                        with self._globalDispatcherLock:
                            if account.busy: continue

                        if len(usedAccounts) >= order.quantity: break

                        with self._globalDispatcherLock:
                            self._blockedServices.append(serviceId)

                            account.busy = True
                            taskId = loadServiceTask(serviceId, account.accountUsername)
                            account.taskId = taskId

                        usedAccounts.append(account)
                        usedAccountSearcher[taskId] = account

                    self._core.processService(serviceId) # push loaded service
                    usedServices.append(serviceId)
                    logger.debug(f'Using new service {serviceId} for {order.id}')


                # getting data from the services
                for serviceId in usedServices:
                    # getting service`s history
                    with self._globalDispatcherLock:
                        data: Optional[list[HistoryObject]] = self._core.serviceHistory(serviceId)
                        if not data: continue

                        # free the service
                        if serviceId in self._blockedServices:
                            self._blockedServices.remove(serviceId)

                    for ho in data:
                        account = usedAccountSearcher.pop(ho.taskId, None)
                        # skip if task id not found
                        if not account: continue
                        self._freeAccount(account)

                        if ho.result is True:
                            totalQuantity -= 1
                            logger.debug(f'Successful used account {account.accountUsername} with {serviceId} for {order.id} order.')
                        else:
                            # deleting account from "successful list" if result is incorrect
                            logger.warning(f'<Order {order.id}> Gotten incorrect task result: {ho}')
                            usedAccounts.remove(account)

        except Exception as e:
            logger.error(f'<Order {order.id}> Error in order processor`s iterator: {e}')
        else:
            logger.info(f'<Order {order.id}> Order successfully completed.')
        finally:
            with self._globalDispatcherLock:
                self._processingOrders.remove(order)

                # if "while" has been interrupted, free all services
                for serviceId in usedServices:
                    if not serviceId in self._blockedServices: continue
                    self._blockedServices.remove(serviceId)

        return True


    @afterLoad
    def _manageOrder(self, order: OrderData):
        """
            Order preprocess function.
            Need to collect all data, change statuses, log etc.
            Start all process order in new thread.
        """

        # if we don`t need to process this order
        if order.service_id not in list(self._sellingScripts.keys()): return

        self._panelManager.saveOrder(order)

        # you can use pure threads because orders won`t be completed if all farm is busy (IO-BOUND only tasks)
        threading.Thread(
            target=self._processOrder,
            args=(order, self._sellingScripts[order.service_id], order.link),
        ).start()

        logger.info(
            f'Order {order.id} accepted. ' +
            f'( ${order.price} - {order.quantity} of {order.service_id} for {order.link} )'
        )


    @afterLoad
    def handler(self):
        logger.info('Orders handler started.')

        # base order, use it to handle all orders after this one
        self._panelManager.getFirstOrder()

        while True:
            newOrders: list[OrderData] = self._panelManager.getNewOrders()

            for order in newOrders:
                # making tasks
                self._manageOrder(order)

            time.sleep(self._orderProcessorDelay * 5)