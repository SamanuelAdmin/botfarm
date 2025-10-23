from data.base import Base

from sqlalchemy.orm import Mapped, mapped_column


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    externel_id: Mapped[str] = mapped_column(primary_key=True)
    link: Mapped[str]
    quantity: Mapped[int]
    service_id: Mapped[int]
    service_type: Mapped[str]
    price: Mapped[int]


