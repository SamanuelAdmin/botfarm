from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base


class ConnectedEmail(Base):
    __tablename__ = 'connected_email'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    email: str = Column(String, nullable=False)
    password: str = Column(String, nullable=False)
    account = mapped_column(Integer, ForeignKey("account.id"))
    account_rel: Mapped["Account"] = relationship("Account", back_populates="connected_emails")

    def __init__(self, email, password, *args, **kwargs):
        self.email = email
        self.password = password

        super().__init__()

    def __str__(self):
        return '\n'.join([
            f'{col.name} : {getattr(self, col.name)}' for col in self.__table__.columns
        ])


class ConnectedEmailSchemeCreate(BaseModel):
    email: str
    password: str

    class Config: orm_mode = True


class ConnectedEmailSchemeUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None

    class Config: orm_mode = True
