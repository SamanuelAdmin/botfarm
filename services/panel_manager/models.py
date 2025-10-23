from dataclasses import dataclass
from datetime import datetime


@dataclass
class OrderData:
    id: int
    external_id: str
    price: int
    link: str
    quantity: int
    service_id: int
    service_type: str
    created_date: datetime
