"""
Custom exceptions for QuantaRoute Geocoding SDK
"""


class QuantaRouteError(Exception):
    """Base exception for all QuantaRoute errors"""
    pass


class APIError(QuantaRouteError):
    """Raised when API returns an error response"""
    
    def __init__(self, message: str, status_code: int = None, error_code: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded"""
    
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message, status_code=429, error_code="RATE_LIMIT_EXCEEDED")
        self.retry_after = retry_after


class AuthenticationError(APIError):
    """Raised when API key is invalid or missing"""
    
    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(message, status_code=401, error_code="AUTHENTICATION_ERROR")


class ValidationError(QuantaRouteError):
    """Raised when input validation fails"""
    pass


class OfflineProcessingError(QuantaRouteError):
    """Raised when offline processing fails"""
    pass
