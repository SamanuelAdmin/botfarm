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


class AdbHubNotFound(Exception): pass
class AdbHubAlreadyExists(Exception): pass

class OrderAlreadyExists(Exception): pass

class PanelParserServiceError(Exception):
    """Some error in PanelParserService"""

class ValidateJsonError(PanelParserServiceError):
    """Json is not valid"""

class PanelApiServiceError(Exception):
    """Some error in work panel api service"""

class UnknownMethodError(PanelApiServiceError):
    """Set method is unknown"""


class PanelManagerError(Exception):
    """Some exception in PanelManager"""

class NoLastOrder(PanelManagerError):
    """No last order for parse new orders"""
