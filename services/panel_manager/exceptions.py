class PanelParserServiceError(Exception):
    """Some error in PanelParserService"""

class ValidateJsonError(PanelParserServiceError):
    """Json is not valid"""

class PanelApiServiceError(Exception):
    """Some error in work panel api service"""

class UnknownMethodError(PanelApiServiceError):
    """Set method is unknown"""
