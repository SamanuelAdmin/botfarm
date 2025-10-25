from enum import Enum


class OrderStatus(Enum):
# pending
# in_progress
# processing
# completed
# partial
# canceled
# error
# fail
    pending = 'pending'
    in_progress = 'in_progress'
    proccessing = 'proccessing'
    completed = 'completed'
    partial = 'partial'
    canceled = 'canceled'
    error = 'error'
    fail = 'fail'
