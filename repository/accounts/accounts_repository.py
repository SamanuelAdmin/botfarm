from typing import Any, Type

from db.data.base import Base
from db.data.account import Account
from db.data.connected_email import ConnectedEmail
from db.data.device_id import DeviceID

from db.controller import DatabaseController
from meta.crud import CRUD


class AccountsRepository(CRUD):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.controller = DatabaseController()

    def create(
            self, account: Account, device_id: DeviceID, connected_emails: list[ConnectedEmail]
    ) -> None:
        self.controller.add(device_id)
        for ce in connected_emails:
            self.controller.add(ce)

        self.controller.add(account)

    def readAllAccounts(self) -> Any:
        return self.controller.session.query(Account).all()

    def read(self, model: [Type[Base]], id: int) -> Any:
        return self.controller.session.get(model, id)

    def findBy(self, model: [Type[Base]], **kwargs) -> Any:
        return self.controller.session.query(model) \
                .filter_by(**kwargs).one()

    def findAllBy(self, model: [Type[Base]], **kwargs) -> Any:
        return self.controller.session.query(model) \
                .filter_by(**kwargs)

    def update(self, model: [Type[Base]], id, **kwargs) -> None:
        obj = self.controller.session.get(model, id)
        for k, v in kwargs.items():
            setattr(obj, k, v)
        self.controller.save()

    def delete(self, id: int) -> None:
        self.controller.delete(
            self.controller.session.get(Account, id)
        )