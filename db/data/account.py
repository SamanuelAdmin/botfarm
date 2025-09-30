from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, PickleType
from sqlalchemy.orm import relationship, Mapped

from .device_id import *
from .connected_email import *

from .base import Base


class Account(Base):
    __tablename__ = 'account'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    login: str = Column(String, nullable=False)
    password: str = Column(String, nullable=False)
    key: str = Column(String, nullable=False)
    user_agent: str = Column(String, nullable=False)
    cookies: dict[str, str] = Column(PickleType)

    device_id: Mapped[DeviceID] = relationship(
        "DeviceID",
        cascade="all, delete",
        uselist=False,
        # primaryjoin="Account.id == DeviceID.account",
        back_populates="account_rel"
    )

    connected_emails: Mapped[list[ConnectedEmail]] = relationship(
        "ConnectedEmail",
        cascade="all, delete",
        # primaryjoin="Account.id == ConnectedEmail.account",
        back_populates="account_rel"
    )


    def __str__(self):
        return '\n'.join([
            f'{col.name} : {getattr(self, col.name)}' for col in self.__table__.columns
        ])


class AccountSchemeCreate(BaseModel):
    login: str
    password: str
    key: str
    user_agent: str
    cookies: dict[str, str]
    device_id: DeviceIDSchemeCreate
    connected_emails: list[ConnectedEmailSchemeCreate]

    class Config: from_attributes = True


class AccountSchemeUpdate(BaseModel):
    login: Optional[str] = None
    password: Optional[str] = None
    key: Optional[str] = None
    user_agent: Optional[str] = None
    cookies: Optional[dict[str, str]] = None
    device_id: Optional[DeviceIDSchemeUpdate] = None
    connected_emails: Optional[list[ConnectedEmailSchemeUpdate]] = None

    class Config: from_attributes = True