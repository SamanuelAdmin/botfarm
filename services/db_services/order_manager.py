from db.data.order import Order

from meta.schemas import OrderModel
from repository.repository import Repository

from meta.exceptions import OrderAlreadyExists


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

    def add(self, order: OrderModel) -> None: 
        if self.exists(order.id):
            raise OrderAlreadyExists("This order already exists")

        self.repository.create(
            Order( **order.model_dump() )
        )

    def getLastOrder(self) -> Order|None:
        """Get last added order"""
        #TODO:May be need sort by date after get? 
        return self.repository.getLast(Order, Order.created_date.desc())

    def delete(self, id: int) -> None:
        self.repository.delete(Order, id)
         


