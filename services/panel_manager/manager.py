import datetime
from services.db_services.order_manager import OrderManager
from services.panel_manager.api_service import PanelApiService
from services.panel_manager.models import OrderData
from services.panel_manager.parser_service import PanelParserService


class PanelManager():
    """
        There will be bussines logic for panel manager.
        Manage api_service and parser_service for get new orders, every 15 seconds for example.
    """
    def __init__(self, orderManager: OrderManager, apiKey: str):
        self._parserService = PanelParserService()
        self._apiService = PanelApiService(apiKey)
        self._orderManager = orderManager

    def getFirstOrder(self) -> OrderData:
        api_json = self._apiService.getSortedOrders()
        orders_list = self._parserService.parseOrdersJson(api_json)
        return orders_list[0]

    def getNewOrders(self) -> list[OrderData]:
        """
            Gets orders starting from the last one
        """
        last_order = self._orderManager.getLastOrder()
        created_timestamp = last_order.created_date.timestamp()

        #WARN: This part can go to new parser service
        apiJson = self._apiService.getOrdersJsonCreatedFrom(created_timestamp)
        return self._parserService.parseOrdersJson(apiJson)


        

        
