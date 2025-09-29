from typing import Any, Type

from db.data.base import Base

from db.controller import DatabaseController
from meta.crud import CRUD
from meta.singleton import Singleton


class Repository(CRUD, metaclass=Singleton):
    """
        Repository class is middle layer between
        database controller and services.
        Release all CRUD operations + custom methods.
    """

    def __init__(self):
        self.controller = DatabaseController()

    def create(self, *args) -> None:
        '''
            Recursive adding obj to database
        '''

        for obj in args:
            if isinstance(obj, list) or isinstance(obj, tuple):
                self.create(*obj)
            else:
                self.controller.add(obj)


    def read(self, model: Type[Base], _id: int) -> Any:
        return self.controller.session.get(model, _id)

    def update(self, model: Type[Base], _id, **kwargs) -> None:
        obj = self.controller.session.get(model, _id)
        for k, v in kwargs.items():
            setattr(obj, k, v)
        self.controller.save()

    def delete(self, model: Type[Base], _id: int) -> None:
        self.controller.delete(
            self.controller.session.get(model, _id)
        )

    # Custom methods

    def readAll(self, model: Type[Base]) -> Any:
        return self.controller.session.query(model).all()

    def findBy(self, model: Type[Base], **kwargs) -> Any:
        return self.controller.session.query(model) \
                .filter_by(**kwargs).first()

    def findAllBy(self, model: Type[Base], **kwargs) -> Any:
        return self.controller.session.query(model) \
                .filter_by(**kwargs).all()
