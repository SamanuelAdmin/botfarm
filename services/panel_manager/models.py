from dataclasses import dataclass
from datetime import datetime


@dataclass
class OrderData:
    id: int
    price: float
    link: str
    quantity: int
    service_id: int
    service_type: str
    created_date: datetime
    created_timestamp: int
