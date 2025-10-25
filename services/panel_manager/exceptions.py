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