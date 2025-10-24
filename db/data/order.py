import datetime
from db.data.base import Base

from sqlalchemy.orm import Mapped, mapped_column


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str]
    quantity: Mapped[int]
    created_date: Mapped[datetime.datetime]
    created_timestamp: Mapped[int]
    service_id: Mapped[int]
    service_type: Mapped[str]
    price: Mapped[float]

    is_new: Mapped[bool] = mapped_column(default=True)

