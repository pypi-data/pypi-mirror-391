"""
Exception Classes for BottleOCR Library
=======================================

Custom exceptions for better error handling and debugging.
"""


class BottleOCRError(Exception):
    """Base exception class for all BottleOCR errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """
        Initialize BottleOCR error.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or 'UNKNOWN_ERROR'
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """Convert error to dictionary representation."""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details
        }


class AuthenticationError(BottleOCRError):
    """Raised when API key authentication fails."""
    
    def __init__(self, message: str, error_code: str = 'AUTH_FAILED', details: dict = None):
        super().__init__(message, error_code, details)


class ValidationError(BottleOCRError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, error_code: str = 'VALIDATION_FAILED', details: dict = None):
        super().__init__(message, error_code, details)


class OCRProcessingError(BottleOCRError):
    """Raised when OCR processing fails."""
    
    def __init__(self, message: str, error_code: str = 'OCR_FAILED', details: dict = None):
        super().__init__(message, error_code, details)


class ExtractionError(BottleOCRError):
    """Raised when prescription extraction fails."""
    
    def __init__(self, message: str, error_code: str = 'EXTRACTION_FAILED', details: dict = None):
        super().__init__(message, error_code, details)


class ConfigurationError(BottleOCRError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, error_code: str = 'CONFIG_ERROR', details: dict = None):
        super().__init__(message, error_code, details)


class RateLimitError(BottleOCRError):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str, error_code: str = 'RATE_LIMITED', details: dict = None):
        super().__init__(message, error_code, details)


class QuotaExceededError(BottleOCRError):
    """Raised when usage quota is exceeded."""
    
    def __init__(self, message: str, error_code: str = 'QUOTA_EXCEEDED', details: dict = None):
        super().__init__(message, error_code, details)


class NetworkError(BottleOCRError):
    """Raised when network operations fail."""
    
    def __init__(self, message: str, error_code: str = 'NETWORK_ERROR', details: dict = None):
        super().__init__(message, error_code, details)


class TimeoutError(BottleOCRError):
    """Raised when operations timeout."""
    
    def __init__(self, message: str, error_code: str = 'TIMEOUT', details: dict = None):
        super().__init__(message, error_code, details)