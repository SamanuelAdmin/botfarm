from db.data.order import Order

from repository.repository import Repository

from exceptions import OrderAlreadyExists


class AccountsManager:
    """
        Working with the order table
    """

    def __init__(self):
        self.repository = Repository()

    def exists(self, id: int) -> bool:
        return bool(
            self.repository.read(Order, id)
        )

    def add(
        self,
        id: int, externel_id: int, link: str,
        quantity: int, service_id: int,
        service_type: str, price: int
    ) -> None: 
        if self.exists(id):
            raise OrderAlreadyExists("This order already exists")

        self.repository.create(
            Order(
                id, externel_id,
                link, quantity,
                service_id, service_type, price
            )
        )

    def getLastOrder(self) -> Order|None:
        """Get last added order"""
        return self.repository.getLastOrder()

    def delete(self, id: int) -> None:
        self.repository.delete(Order, id)
         


