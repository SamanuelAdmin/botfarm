import datetime
from data.base import Base

from sqlalchemy.orm import Mapped, mapped_column


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(primary_key=True)
    link: Mapped[str]
    quantity: Mapped[int]
    created_date: Mapped[datetime.datetime]
    service_id: Mapped[int]
    service_type: Mapped[str]
    price: Mapped[int]


