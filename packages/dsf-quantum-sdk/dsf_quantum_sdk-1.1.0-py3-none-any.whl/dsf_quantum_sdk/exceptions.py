# dsf_quantum_sdk/exceptions.py
"""Custom exceptions for DSF Quantum SDK"""


class QuantumSDKError(Exception):
    """Base exception for all SDK errors"""
    pass


class ValidationError(QuantumSDKError):
    """Raised when input validation fails"""
    pass


class APIError(QuantumSDKError):
    """Raised when API request fails"""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class RateLimitError(APIError):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str, retry_after: int = 60, limit: int = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after
        self.limit = limit