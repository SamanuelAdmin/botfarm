from services.panel_manager.manager import PanelManager


class Dispatcher:
    """
        Main manager for moderate orders, process it and manage accounts.
        New abstract layer for the system.
    """

    def __init__(self, panelManager: PanelManager):
        self._panelManager = panelManager


    def update(self):
        """
            Update function for orders.
            Getting new orders via manager.
        """

        newOrders = self._panelManager.getNewOrders()
