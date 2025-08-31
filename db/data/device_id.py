from typing import Optional

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from pydantic import BaseModel

from .base import Base



class DeviceID(Base):
    __tablename__ = 'device_id'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    device_id: str = Column(String, nullable=False)
    uuid: str = Column(String, nullable=False)
    session_id: str = Column(String, nullable=False)
    phone_id: str = Column(String, nullable=False)
    account = mapped_column(Integer, ForeignKey("account.id"))
    account_rel: Mapped["Account"] = relationship("Account", back_populates="device_id")

    def __init__(self, device_id, uuid, session, phone_id, *args, **kwargs):
        self.device_id = device_id
        self.uuid = uuid
        self.session_id = session
        self.phone_id = phone_id

        super().__init__()

    def __str__(self):
        return '\n'.join([
            f'{col.name} : {getattr(self, col.name)}' for col in self.__table__.columns
        ])


class DeviceIDSchemeCreate(BaseModel):
    device_id: str
    uuid: str
    session_id: str
    phone_id: str

    class Config: orm_mode = True


class DeviceIDSchemeUpdate(BaseModel):
    device_id: Optional[str] = None
    uuid: Optional[str] = None
    session_id: Optional[str] = None
    phone_id: Optional[str] = None

    class Config: orm_mode = True