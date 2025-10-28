from enum import StrEnum


class OrderStatus(StrEnum):
    pending = 'pending'
    in_progress = 'in_progress'
    proccessing = 'proccessing'
    completed = 'completed'
    partial = 'partial'
    canceled = 'canceled'
    error = 'error'
    fail = 'fail'
