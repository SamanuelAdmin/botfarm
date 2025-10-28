import time

from meta.exceptions import NoLastOrder

from services.db_services.order_manager import OrderManager
from services.panel_manager.api_service import PanelApiService
from services.panel_manager.models import OrderData
from services.panel_manager.parser_service import PanelParserService



class PanelManager:
    """
        Panel manager - manager for all logic for getting and saving orders.
        Manage api_service and parser_service for get new orders, every 15 seconds for example.
    """
    def __init__(self, orderManager: OrderManager, apiKey: str):
        self._parserService = PanelParserService()
        self._apiService = PanelApiService(apiKey)
        self._orderManager = orderManager
        self._parserState = False

    def getFirstOrder(self) -> None:
        api_json = self._apiService.getSortedOrders()
        orders_list = self._parserService.parseOrdersJson(api_json)

        order = orders_list[0]
        if self._orderManager.exists(order.id): 
            return
        self._orderManager.createOrder(order)

    def getNewOrders(self) -> list[OrderData]:
        """
            Gets orders starting from the last one.
            Use it to easily parsing new orders.
        """
        last_order = self._orderManager.getLastOrder()
        if not last_order: raise NoLastOrder

        #WARN: This part can go to new parser service
        apiJson = self._apiService.getOrdersJsonCreatedFrom(last_order.created_timestamp)
        parsed = self._parserService.parseOrdersJson(apiJson)

        return parsed[1:]

    def stopParser(self) -> None:
        self._parserState = False

    def saveOrder(self, order: OrderData) -> None:
        self._orderManager.createOrder(order)

    
    def startParse(self, parsingDelay: int = 15, do_not_use_in_production: bool = False) -> None:
        """
            Test method, this functions will be in the order`s dispatcher.
            Do not use this in production because you cannot moderate order with this code.
            If you test it via tests.py file or another test case - please, set
            do_not_use_in_production = True
            to avoid exceptions.

            Parsing while parserState is True
        """
        if __name__ != "__main__" and not do_not_use_in_production:
            raise Exception('For tests only! Do not use in production!')

        self._parserState = True
        self.getFirstOrder()

        while self._parserState:
            new_orders: list[OrderData] = self.getNewOrders()

            for order in new_orders:
                self.saveOrder(order)
                print(f"New order: {order.service_type} | {order.created_date.strftime('%y-%m-%d %H:%M:%S')} | {order.link} | {order.price} | {order.quantity}")

            time.sleep(parsingDelay)

        
