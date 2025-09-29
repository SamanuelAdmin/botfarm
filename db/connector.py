from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from meta.singleton import Singleton

from .data.base import Base


class DatabaseConnector:
    __metaclass__ = Singleton

    def __init__(self, filename="database.db", echo=False):
        self._engine = create_engine(f"sqlite+pysqlite:///{filename}", echo=echo)
        self._asyncEngine = create_async_engine(f"sqlite+aiosqlite:///{filename}", echo=echo)

        self._SessionMaker = sessionmaker(bind=self._engine)
        self._session = self._SessionMaker()


    def __del__(self):
        self._session.close()

    @property
    def session(self): return self._session

    async def getAsyncSession(self):
        async with AsyncSession(self._asyncEngine) as session:
            yield session

    def create_all(self):
        Base().metadata.create_all(self._engine)
