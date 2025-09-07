from app.config.exceptions import BaseAppException

class UserNotFoundError(BaseAppException):
    """Raised when user is not found"""
    def __init__(self, message: str = "User not found"):
        super().__init__(message, "USER_NOT_FOUND")

class EmailAlreadyExistsError(BaseAppException):
    """Raised when email already exists"""
    def __init__(self, message: str = "Email already exists"):
        super().__init__(message, "EMAIL_EXISTS")

class InvalidCredentialsError(BaseAppException):
    """Raised when credentials are invalid"""
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message, "INVALID_CREDENTIALS")

class AccountLockedError(BaseAppException):
    """Raised when account is locked"""
    def __init__(self, message: str = "Account is temporarily locked"):
        super().__init__(message, "ACCOUNT_LOCKED")

class EmailNotVerifiedError(BaseAppException):
    """Raised when email is not verified"""
    def __init__(self, message: str = "Email address is not verified"):
        super().__init__(message, "EMAIL_NOT_VERIFIED")

class InvalidTokenError(BaseAppException):
    """Raised when token is invalid or expired"""
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message, "INVALID_TOKEN")

class InsufficientPermissionsError(BaseAppException):
    """Raised when user lacks required permissions"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "INSUFFICIENT_PERMISSIONS")