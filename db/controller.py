from typing import Any

from meta.singleton import Singleton

if __name__ == "__main__":
    from connector import DatabaseConnector
else: from .connector import DatabaseConnector


class DatabaseController:
    __metaclass__ = Singleton

    def __init__(self, filename: str="database.db"):
        self.connector = DatabaseConnector(filename)
        self.connector.create_all()
        self.session = self.connector.session

    def add(self, obj: Any) -> None:
        self.session.add(obj)
        self.session.commit()

    def delete(self, obj: Any) -> None:
        self.session.delete(obj)
        self.session.commit()

    def save(self):
        self.session.commit()