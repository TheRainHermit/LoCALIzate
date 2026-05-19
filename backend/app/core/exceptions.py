"""
Exceptions module for LoCALIzate Backend
=======================================

Custom exception classes for the application.
Provides standardized error handling with proper HTTP status codes.

Usage:
    from core.exceptions import NotFoundException, ValidationException
    
    raise NotFoundException("Lugar no encontrado")
    raise ValidationException("El rating debe ser entre 1 y 5")
    
    # With custom status code
    raise AppException("Error personalizado", status_code=418)
"""

from typing import Any, Dict, Optional, List, Union
from fastapi import HTTPException, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


# =====================================================
# BASE EXCEPTION
# =====================================================

class AppException(HTTPException):
    """
    Base exception class for all application-specific exceptions.
    
    Attributes:
        status_code: HTTP status code (default: 500)
        detail: Error message
        headers: Optional HTTP headers
        error_code: Internal error code for frontend
        metadata: Additional error context
    """
    
    def __init__(
        self,
        detail: str = "Error interno del servidor",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers: Optional[Dict[str, str]] = None,
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self._generate_error_code(status_code)
        self.metadata = metadata or {}
    
    def _generate_error_code(self, status_code: int) -> str:
        """Generate an internal error code based on status code."""
        error_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_ERROR",
            503: "SERVICE_UNAVAILABLE"
        }
        return error_map.get(status_code, "UNKNOWN_ERROR")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": self.detail,
                "status_code": self.status_code,
                "metadata": self.metadata
            }
        }


# =====================================================
# HTTP EXCEPTIONS (4xx)
# =====================================================

class BadRequestException(AppException):
    """Exception for bad requests (400)."""
    
    def __init__(
        self,
        detail: str = "Solicitud inválida",
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code or "BAD_REQUEST",
            metadata=metadata
        )


class UnauthorizedException(AppException):
    """Exception for unauthorized access (401)."""
    
    def __init__(
        self,
        detail: str = "No autenticado",
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code or "UNAUTHORIZED",
            metadata=metadata
        )


class ForbiddenException(AppException):
    """Exception for forbidden access (403)."""
    
    def __init__(
        self,
        detail: str = "No tienes permisos para esta acción",
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code or "FORBIDDEN",
            metadata=metadata
        )


class NotFoundException(AppException):
    """Exception for resources not found (404)."""
    
    def __init__(
        self,
        detail: str = "Recurso no encontrado",
        resource_type: Optional[str] = None,
        resource_id: Optional[Union[str, int]] = None,
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        # Build a more descriptive message if resource info is provided
        if resource_type and resource_id:
            detail = f"{resource_type} con ID '{resource_id}' no encontrado"
        elif resource_type:
            detail = f"{resource_type} no encontrado"
        
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=error_code or "NOT_FOUND",
            metadata={
                **(metadata or {}),
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )


class ConflictException(AppException):
    """Exception for resource conflicts (409)."""
    
    def __init__(
        self,
        detail: str = "Conflicto con el estado actual del recurso",
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            error_code=error_code or "CONFLICT",
            metadata=metadata
        )


class ValidationException(AppException):
    """Exception for validation errors (422)."""
    
    def __init__(
        self,
        detail: str = "Error de validación",
        errors: Optional[List[Dict[str, Any]]] = None,
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=error_code or "VALIDATION_ERROR",
            metadata={
                **(metadata or {}),
                "validation_errors": errors or []
            }
        )


class RateLimitException(AppException):
    """Exception for rate limit exceeded (429)."""
    
    def __init__(
        self,
        detail: str = "Demasiadas solicitudes. Intenta más tarde.",
        retry_after: Optional[int] = 60,
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        headers = {"Retry-After": str(retry_after)} if retry_after else None
        super().__init__(
            detail=detail,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers=headers,
            error_code=error_code or "RATE_LIMIT_EXCEEDED",
            metadata={
                **(metadata or {}),
                "retry_after": retry_after
            }
        )


# =====================================================
# BUSINESS LOGIC EXCEPTIONS
# =====================================================

class BusinessException(AppException):
    """Base exception for business logic errors."""
    
    def __init__(
        self,
        detail: str = "Error de negocio",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            detail=detail,
            status_code=status_code,
            error_code=error_code or "BUSINESS_ERROR",
            metadata=metadata
        )


class DuplicateResourceException(BusinessException):
    """Exception when trying to create a duplicate resource."""
    
    def __init__(
        self,
        resource_type: str,
        field: str,
        value: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        detail = f"Ya existe un {resource_type} con {field} '{value}'"
        super().__init__(
            detail=detail,
            error_code="DUPLICATE_RESOURCE",
            metadata={
                **(metadata or {}),
                "resource_type": resource_type,
                "field": field,
                "value": value
            }
        )


class InvalidOperationException(BusinessException):
    """Exception for invalid operations."""
    
    def __init__(
        self,
        operation: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        detail = f"No se puede realizar '{operation}': {reason}"
        super().__init__(
            detail=detail,
            error_code="INVALID_OPERATION",
            metadata={
                **(metadata or {}),
                "operation": operation,
                "reason": reason
            }
        )


class InsufficientPermissionsException(BusinessException):
    """Exception for insufficient permissions."""
    
    def __init__(
        self,
        action: str,
        resource: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        detail = f"No tienes permisos para {action} en {resource}"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="INSUFFICIENT_PERMISSIONS",
            metadata={
                **(metadata or {}),
                "action": action,
                "resource": resource
            }
        )


class ResourceLimitExceededException(BusinessException):
    """Exception when user exceeds a resource limit."""
    
    def __init__(
        self,
        resource_type: str,
        limit: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        detail = f"Has alcanzado el límite de {limit} {resource_type}"
        super().__init__(
            detail=detail,
            error_code="RESOURCE_LIMIT_EXCEEDED",
            metadata={
                **(metadata or {}),
                "resource_type": resource_type,
                "limit": limit
            }
        )


# =====================================================
# SERVICE EXCEPTIONS
# =====================================================

class ExternalServiceException(AppException):
    """Exception for external service errors."""
    
    def __init__(
        self,
        service_name: str,
        detail: str = "Error en servicio externo",
        status_code: int = status.HTTP_502_BAD_GATEWAY,
        original_error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            detail=f"{service_name}: {detail}",
            status_code=status_code,
            error_code="EXTERNAL_SERVICE_ERROR",
            metadata={
                **(metadata or {}),
                "service": service_name,
                "original_error": original_error
            }
        )


class GeocodingException(ExternalServiceException):
    """Exception for geocoding service errors."""
    
    def __init__(
        self,
        address: str,
        detail: str = "No se pudo geocodificar la dirección",
        original_error: Optional[str] = None
    ):
        super().__init__(
            service_name="Geocoding",
            detail=f"Dirección '{address}': {detail}",
            original_error=original_error,
            metadata={"address": address}
        )


class RoutingException(ExternalServiceException):
    """Exception for routing/OSRM service errors."""
    
    def __init__(
        self,
        detail: str = "No se pudo calcular la ruta",
        coordinates: Optional[List[tuple]] = None,
        original_error: Optional[str] = None
    ):
        super().__init__(
            service_name="OSRM Routing",
            detail=detail,
            original_error=original_error,
            metadata={"coordinates": coordinates}
        )


class AIException(ExternalServiceException):
    """Exception for AI/Chat service errors."""
    
    def __init__(
        self,
        detail: str = "Error en el asistente virtual",
        original_error: Optional[str] = None
    ):
        super().__init__(
            service_name="AI Assistant",
            detail=detail,
            original_error=original_error
        )


# =====================================================
# DATABASE EXCEPTIONS
# =====================================================

class DatabaseException(AppException):
    """Exception for database errors."""
    
    def __init__(
        self,
        detail: str = "Error en la base de datos",
        operation: Optional[str] = None,
        table: Optional[str] = None,
        original_error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            metadata={
                **(metadata or {}),
                "operation": operation,
                "table": table,
                "original_error": original_error
            }
        )


# =====================================================
# EXCEPTION HANDLER
# =====================================================

async def handle_exception(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Global exception handler for FastAPI.
    
    Converts various exception types to standardized JSON responses.
    
    Usage in main.py:
        app.add_exception_handler(Exception, handle_exception)
    """
    # Handle our custom exceptions
    if isinstance(exc, AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
            headers=exc.headers
        )
    
    # Handle HTTPException from FastAPI
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "status_code": exc.status_code
                }
            },
            headers=exc.headers
        )
    
    # Handle validation errors from Pydantic
    if hasattr(exc, "errors") and callable(getattr(exc, "errors")):
        # This is a Pydantic validation error
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Error de validación de datos",
                    "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "metadata": {
                        "validation_errors": exc.errors() if hasattr(exc, "errors") else []
                    }
                }
            }
        )
    
    # Handle any other exception (unexpected)
    # Log the error here if you have a logger
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Error interno del servidor",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "metadata": {
                    "exception_type": type(exc).__name__
                }
            }
        }
    )


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def is_app_exception(exc: Exception) -> bool:
    """Check if an exception is an AppException."""
    return isinstance(exc, AppException)


def get_exception_status_code(exc: Exception) -> int:
    """Get HTTP status code from an exception."""
    if isinstance(exc, AppException):
        return exc.status_code
    if isinstance(exc, HTTPException):
        return exc.status_code
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def get_exception_message(exc: Exception) -> str:
    """Get error message from an exception."""
    if isinstance(exc, AppException):
        return exc.detail
    if isinstance(exc, HTTPException):
        return str(exc.detail)
    return str(exc)


# =====================================================
# EXPORTS
# =====================================================

__all__ = [
    # Base
    "AppException",
    
    # HTTP Exceptions (4xx)
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "ConflictException",
    "ValidationException",
    "RateLimitException",
    
    # Business Exceptions
    "BusinessException",
    "DuplicateResourceException",
    "InvalidOperationException",
    "InsufficientPermissionsException",
    "ResourceLimitExceededException",
    
    # Service Exceptions
    "ExternalServiceException",
    "GeocodingException",
    "RoutingException",
    "AIException",
    
    # Database Exceptions
    "DatabaseException",
    
    # Utilities
    "handle_exception",
    "is_app_exception",
    "get_exception_status_code",
    "get_exception_message",
]


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("Exceptions module loaded successfully")
    
    # Test exceptions
    try:
        raise NotFoundException("Lugar", 123)
    except NotFoundException as e:
        print(f"Test 1 - NotFoundException: {e.to_dict()}")
    
    try:
        raise ValidationException(
            "Error de validación",
            errors=[{"field": "rating", "message": "Debe ser entre 1 y 5"}]
        )
    except ValidationException as e:
        print(f"Test 2 - ValidationException: {e.to_dict()}")
    
    try:
        raise RateLimitException(retry_after=30)
    except RateLimitException as e:
        print(f"Test 3 - RateLimitException: {e.to_dict()}")
    
    print("\n✅ Todas las excepciones funcionan correctamente")