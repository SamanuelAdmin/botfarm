from dataclasses import dataclass

from services.panel_manager.manager import PanelManager



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

    def __init__(self, panelManager: PanelManager):
        self._panelManager = panelManager


    def update(self):
        """
            Update function for orders.
            Getting new orders via manager.
        """

        newOrders = self._panelManager.getNewOrders()


    def load(self):
        """
            Function for starting all loading processes.
            Getting all active accounts.
        """



