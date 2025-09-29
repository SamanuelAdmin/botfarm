from pydantic import BaseModel
from sqlalchemy import Column, String

from .base import Base


class AdbHub(Base):
    __tablename__ = 'adb_hub'

    id: int = Column(String, primary_key=True, autoincrement=False)
    apiLink: str = Column(String, nullable=False)

    def __str__(self):
        return '\n'.join([
            f'{col.name} : {getattr(self, col.name)}' for col in self.__table__.columns
        ])


class ConnectedEmailSchemeCreate(BaseModel):
    apiLink: str

    class Config: orm_mode = True


class ConnectedEmailSchemeUpdate(BaseModel):
    apiLink: str

    class Config: orm_mode = True
