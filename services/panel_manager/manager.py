from meta.exceptions import OrderAlreadyExists
from meta.schemas import OrderModel
from services.db_services.order_manager import OrderManager
from services.panel_manager.api_service import PanelApiService
from services.panel_manager.models import OrderData
from services.panel_manager.parser_service import PanelParserService

from dataclasses import asdict

import time


class PanelManagerError(Exception):
    """Some exception in PanelManager"""

class NoLastOrder(PanelManagerError):
    """No last order for parse new orders"""


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
        self._orderManager.add(
            OrderModel(
                id=orders_list[0].id,
                link=orders_list[0].link,
                quantity=orders_list[0].quantity,
                created_date=orders_list[0].created_date,
                created_timestamp=orders_list[0].created_timestamp,
                service_id=orders_list[0].service_id,
                service_type=orders_list[0].service_type,
                price=orders_list[0].price,
            )
        )
        return orders_list[0]

    def getNewOrders(self) -> list[OrderData]:
        """
            Gets orders starting from the last one
        """
        last_order = self._orderManager.getLastOrder()
        if not last_order:
            raise NoLastOrder
        print(last_order.created_date)

        #WARN: This part can go to new parser service
        apiJson = self._apiService.getOrdersJsonCreatedFrom(last_order.created_timestamp)
        parsed = self._parserService.parseOrdersJson(apiJson)
        if len(parsed) == 1: return []
        return parsed[1:]
    
    def start(self) -> None:
        while True:
            new = self.getNewOrders()
            for order in new:
                try:
                    self._orderManager.add(
                        OrderModel(
                            id=order.id,
                            link=order.link,
                            quantity=order.quantity,
                            created_date=order.created_date,
                            created_timestamp=order.created_timestamp,
                            service_id=order.service_id,
                            service_type=order.service_type,
                            price=order.price,
                        )
                    )
                    print(f"New order: {order.service_type} | {order.created_date.strftime('%y-%m-%d %H:%M:%S')} | {order.link} | {order.price} | {order.quantity}")
                except OrderAlreadyExists: continue

            time.sleep(15)



        

        
