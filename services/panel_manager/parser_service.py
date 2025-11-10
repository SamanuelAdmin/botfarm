from datetime import datetime

from services.panel_manager.models import OrderData, OrderJson, ResponseJson
from meta.exceptions import ValidateJsonError

    
class PanelParserService:
    """Parse a json from Panel Api"""
    @staticmethod
    def parseResponseJson(responseJson: dict) -> ResponseJson:
        return ResponseJson.model_validate(responseJson)

    def _validateOrdersJson(self, responseJson: ResponseJson) -> list[OrderJson]:
        try:
            return [
                OrderJson.model_validate(order) for order in responseJson.data['list']
            ]
        except KeyError:
            raise ValidateJsonError('Does not exist key "list" in json!')

    def _parseOrderJsonToOrderData(self, order: OrderJson) -> OrderData:
        return OrderData(
            id=order.id,
            price=float(order.charge.value),
            link=order.link,
            quantity=order.quantity,
            service_id=order.service_id,
            service_type=order.service_type,
            created_date=order.created_date,
            created_timestamp=order.created_timestamp,
            status=order.status
        )

    def parseOrdersJson(self, responseJson: ResponseJson) -> list[OrderData]:
        """Parses json orders"""
        try:
            orders: list[OrderJson] = self._validateOrdersJson(responseJson)
            orders_data = []
            for order in orders:
                orders_data.append(
                    self._parseOrderJsonToOrderData(order)
                )
            return orders_data
        except KeyError:
            raise ValidateJsonError(f"Json is not valid!")

