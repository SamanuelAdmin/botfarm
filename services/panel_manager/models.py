from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from meta.enums import OrderStatus


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
    status: OrderStatus

@dataclass
class OrderUpdateData:
    id: int
    status: OrderStatus

class ResponseJson(BaseModel):
    data: dict[str, Any]
    error_message: str
    error_code: int

    
