from typing import Any, Type

from db.data.base import Base
from db.data.account import Account
from db.data.connected_email import ConnectedEmail
from db.data.device_id import DeviceID

from db.controller import DatabaseController
from meta.crud import CRUD
from meta.singleton import Singleton


class Repository(CRUD, metaclass=Singleton):
    '''
        Repository class is middle layer between
        database controller and services.
        Release all CRUD operations + custom methods.
    '''

    def __init__(self):
        self.controller = DatabaseController()

    def create(
            self, account: Account, device_id: DeviceID, connected_emails: list[ConnectedEmail]
    ) -> None:
        self.controller.add(device_id)
        for ce in connected_emails:
            self.controller.add(ce)

        self.controller.add(account)

    def read(self, model: [Type[Base]], _id: int) -> Any:
        return self.controller.session.get(model, _id)

    def update(self, model: [Type[Base]], _id, **kwargs) -> None:
        obj = self.controller.session.get(model, _id)
        for k, v in kwargs.items():
            setattr(obj, k, v)
        self.controller.save()

    def delete(self, model: [Type[Base]], _id: int) -> None:
        self.controller.delete(
            self.controller.session.get(model, _id)
        )

    # Custom methods

    def readAllAccounts(self) -> Any:
        return self.controller.session.query(Account).all()

    def findBy(self, model: [Type[Base]], **kwargs) -> Any:
        return self.controller.session.query(model) \
                .filter_by(**kwargs).one()

    def findAllBy(self, model: [Type[Base]], **kwargs) -> Any:
        return self.controller.session.query(model) \
                .filter_by(**kwargs)
