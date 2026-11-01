from typing import Any, Optional


class SentinelAIException(Exception):
    """Base exception for all SentinelAI domain errors."""
    def __init__(self, message: str, status_code: int = 500, detail: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail or message


class AuthenticationError(SentinelAIException):
    def __init__(self, message: str = "Invalid credentials or token expired", detail: Optional[Any] = None):
        super().__init__(message, status_code=401, detail=detail)


class PermissionDeniedError(SentinelAIException):
    def __init__(self, message: str = "Administrator privileges required", detail: Optional[Any] = None):
        super().__init__(message, status_code=403, detail=detail)


class NotFoundError(SentinelAIException):
    def __init__(self, message: str = "Resource not found", detail: Optional[Any] = None):
        super().__init__(message, status_code=404, detail=detail)


class ValidationError(SentinelAIException):
    def __init__(self, message: str = "Invalid input data", detail: Optional[Any] = None):
        super().__init__(message, status_code=422, detail=detail)


class ConflictError(SentinelAIException):
    def __init__(self, message: str = "Resource conflict", detail: Optional[Any] = None):
        super().__init__(message, status_code=409, detail=detail)


class ProtectedTargetError(SentinelAIException):
    def __init__(self, target: str, message: Optional[str] = None):
        msg = message or f"Security violation: Target '{target}' is a protected address/network and cannot be blocked."
        super().__init__(msg, status_code=400, detail={"target": target, "reason": "protected_target"})


class FirewallExecutionError(SentinelAIException):
    def __init__(self, message: str, detail: Optional[Any] = None):
        super().__init__(message, status_code=500, detail=detail)


class ModelNotLoadedError(SentinelAIException):
    def __init__(self, model_name: str, message: Optional[str] = None):
        msg = message or f"ML Model '{model_name}' artifact is not loaded or has not been trained yet."
        super().__init__(msg, status_code=503, detail={"model_name": model_name, "status": "Not Loaded"})
