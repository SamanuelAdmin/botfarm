import datetime
from pydantic import BaseModel


class OrderModel(BaseModel):
    id: int
    link: str
    quantity: int
    created_date: datetime.datetime
    created_timestamp: int
    service_id: int
    service_type: str
    price: float
