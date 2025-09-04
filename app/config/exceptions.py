

class BaseAppException(Exception):
    """Base exception for application"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class EntityNotFoundError(BaseAppException):
    """Raised when entity not found"""
    pass

class ValidationError(BaseAppException):
    """Raised when validation fails"""
    pass

class PermissionDeniedError(BaseAppException):
    """Raised when permission denied"""
    pass

class BusinessLogicError(BaseAppException):
    """Raised when business logic violation occurs"""
    pass