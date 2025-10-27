from enum import StrEnum


class OrderStatus(StrEnum):
    pending: str = 'pending'
    in_progress: str = 'in_progress'
    proccessing: str = 'proccessing'
    completed: str = 'completed'
    partial: str = 'partial'
    canceled: str = 'canceled'
    error: str = 'error'
    fail: str = 'fail'
