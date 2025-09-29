from fastapi import HTTPException


class AccountNotFoundException(Exception):
    def __init__(self, account_id: int):
        self.account_id = account_id

    def __str__(self): return f'Account with id {self.account_id} not found.'

class AccountNotFoundHttpException(HTTPException):
    __metaclass__ = AccountNotFoundException
    status_code = 404

    def __init__(self, account_id: int):
        self.account_id = account_id
        super().__init__(self.status_code)

    def __str__(self): return f'[HTTP] Account with id {self.account_id} not found.'


class IncorrectDataFormatException(Exception): pass