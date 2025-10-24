from datetime import datetime

from services.panel_manager.models import OrderData
from services.panel_manager.exceptions import ValidateJsonError

    
class PanelParserService:
    """Parse a json from Panel Api"""
    def _parseOrderJson(self, order: dict) -> OrderData:
        return OrderData(
            id=order['id'],
            price=order['charge']['value'],
            link=order['link'],
            quantity=order['quantity'],
            service_id=order['service_id'],
            service_type=order['service_type'],
            created_date=datetime.strptime(order['created'], '%Y-%m-%d %H:%M:%S'),
            created_timestamp=order['created_timestamp']
        )

    def parseOrdersJson(self, apiJson: dict) -> list[OrderData]:
        """Parses json orders"""
        try:
            orders: list[dict] = apiJson['data']['list']
            orders_data = []
            for order in orders:
                orders_data.append(
                    self._parseOrderJson(order)
                )
            return orders_data
        except KeyError:
            raise ValidateJsonError(f"Json is not valid!")

