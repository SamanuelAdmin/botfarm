from dataclasses import asdict
from db.data.order import Order

from meta.schemas import OrderModel
from repository.repository import Repository

from meta.exceptions import OrderAlreadyExists
from services.panel_manager.models import OrderData, OrderUpdateData


class OrderManager:
    """
        Working with the order table
    """

    def __init__(self):
        self.repository = Repository()

    def exists(self, id: int) -> bool:
        return bool(
            self.repository.read(Order, id)
        )

    def createOrder(self, order: OrderData) -> None: 
        if self.exists(order.id):
            raise OrderAlreadyExists("This order already exists")

        self.repository.create(
            Order(
                **OrderModel(
                    **asdict(order)
                ).model_dump()
            )
        )

    def readOrder(self, order_id: int) -> Order | None:
        return self.repository.read(Order, order_id)

    def readAllOrder(self) -> list[Order]:
        return self.repository.readAll(Order)

    def deleteOrder(self, order_id: int) -> None:
        self.repository.delete(Order, order_id)

    def updateOrder(self, order: OrderUpdateData) -> None:
        self.repository.update(
            Order, order.id, **asdict(order)
        )

    def getLastOrder(self) -> Order|None:
        """Get last added order"""
        #TODO:May be need sort by date after get? 
        return self.repository.getLast(Order, Order.created_date.desc())

    def delete(self, id: int) -> None:
        self.repository.delete(Order, id)
         


