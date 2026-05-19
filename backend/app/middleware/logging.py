"""
Logging Middleware for LoCALIzate Backend
========================================

Request/response logging middleware for monitoring and debugging.
Captures request details, response status, and execution time.

Features:
    - Request/response logging with timing
    - Request ID tracking for traceability
    - Sensitive data masking (passwords, tokens)
    - Structured JSON logging for production
    - Configurable log levels

Usage:
    from app.middleware import LoggingMiddleware
    
    # Add to FastAPI app (should be first middleware)
    app.add_middleware(LoggingMiddleware)
"""

import time
import uuid
import json
import logging
from typing import Optional, Dict, Any, List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


# =====================================================
# SENSITIVE DATA MASKING
# =====================================================

# Headers to mask in logs
SENSITIVE_HEADERS = [
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-auth-token",
    "x-refresh-token"
]

# Query parameters to mask
SENSITIVE_QUERY_PARAMS = [
    "token",
    "password",
    "secret",
    "key",
    "api_key",
    "auth_token",
    "refresh_token"
]

# Body fields to mask
SENSITIVE_BODY_FIELDS = [
    "password",
    "token",
    "secret",
    "api_key",
    "authorization",
    "credit_card",
    "card_number",
    "cvv"
]


def mask_sensitive_data(data: str) -> str:
    """
    Mask sensitive data in string.
    
    Args:
        data: String that may contain sensitive data
    
    Returns:
        String with sensitive data masked
    """
    if not data:
        return data
    
    for field in SENSITIVE_BODY_FIELDS:
        # Pattern: "field":"value" or "field": "value"
        import re
        pattern = rf'"{field}"\s*:\s*"[^"]*"'
        replacement = f'"{field}":"[REDACTED]"'
        data = re.sub(pattern, replacement, data, flags=re.IGNORECASE)
        
        # Pattern: field=value
        pattern = rf'{field}=[^&\s]+'
        replacement = f'{field}=[REDACTED]'
        data = re.sub(pattern, replacement, data, flags=re.IGNORECASE)
    
    return data


def mask_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Mask sensitive headers.
    
    Args:
        headers: Original headers dict
    
    Returns:
        Headers dict with sensitive values masked
    """
    masked = {}
    for key, value in headers.items():
        if key.lower() in SENSITIVE_HEADERS:
            masked[key] = "[REDACTED]"
        else:
            masked[key] = value
    return masked


def mask_query_params(query_string: str) -> str:
    """
    Mask sensitive query parameters.
    
    Args:
        query_string: Raw query string
    
    Returns:
        Query string with sensitive params masked
    """
    if not query_string:
        return query_string
    
    parts = query_string.split("&")
    masked_parts = []
    
    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            if key.lower() in SENSITIVE_QUERY_PARAMS:
                masked_parts.append(f"{key}=[REDACTED]")
            else:
                masked_parts.append(part)
        else:
            masked_parts.append(part)
    
    return "&".join(masked_parts)


# =====================================================
# REQUEST ID
# =====================================================

def get_request_id(request: Request) -> str:
    """
    Get or generate request ID for tracing.
    
    Args:
        request: FastAPI request
    
    Returns:
        Request ID string
    """
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
    return request_id


# =====================================================
# LOGGING MIDDLEWARE
# =====================================================

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Request/Response logging middleware.
    
    Logs all requests with method, path, status, and duration.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        log_headers: bool = False,
        log_body: bool = False,
        log_response_body: bool = False
    ):
        """
        Initialize logging middleware.
        
        Args:
            app: ASGI application
            log_headers: Whether to log request headers
            log_body: Whether to log request body (be careful with large bodies)
            log_response_body: Whether to log response body
        """
        super().__init__(app)
        self.log_headers = log_headers
        self.log_body = log_body
        self.log_response_body = log_response_body
        
        logger.info("LoggingMiddleware initialized")
        logger.debug(f"Log headers: {log_headers}, Log body: {log_body}")
    
    async def _log_request(self, request: Request, request_id: str):
        """
        Log request details.
        
        Args:
            request: FastAPI request
            request_id: Unique request ID
        """
        # Basic request info
        log_data = {
            "event": "request",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_string": mask_query_params(str(request.url.query)),
            "client_host": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
        }
        
        # Add headers if enabled
        if self.log_headers:
            log_data["headers"] = mask_headers(dict(request.headers))
        
        # Log at INFO level
        logger.info(json.dumps(log_data))
    
    async def _log_response(
        self,
        request: Request,
        response: Response,
        request_id: str,
        start_time: float,
        error: Optional[Exception] = None
    ):
        """
        Log response details.
        
        Args:
            request: FastAPI request
            response: FastAPI response
            request_id: Unique request ID
            start_time: Request start time
            error: Exception if occurred
        """
        duration_ms = (time.time() - start_time) * 1000
        
        log_data = {
            "event": "response",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code if response else 500,
            "duration_ms": round(duration_ms, 2),
            "duration_formatted": f"{duration_ms:.2f}ms"
        }
        
        # Add error if present
        if error:
            log_data["error"] = str(error)
            log_data["error_type"] = type(error).__name__
        
        # Add response headers if enabled
        if self.log_headers and response:
            log_data["response_headers"] = mask_headers(dict(response.headers))
        
        # Determine log level based on status
        if response and response.status_code >= 500:
            logger.error(json.dumps(log_data))
        elif response and response.status_code >= 400:
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))
    
    async def _get_request_body(self, request: Request) -> Optional[str]:
        """
        Get request body for logging.
        
        Args:
            request: FastAPI request
        
        Returns:
            Request body string or None
        """
        if not self.log_body:
            return None
        
        try:
            # Read body
            body = await request.body()
            
            # Restore body for downstream
            async def receive():
                return {"type": "http.request", "body": body}
            
            request._receive = receive
            
            if body:
                # Try to decode as JSON
                try:
                    body_str = body.decode("utf-8")
                    return mask_sensitive_data(body_str)
                except UnicodeDecodeError:
                    return "[BINARY DATA]"
            
        except Exception as e:
            logger.warning(f"Could not read request body: {str(e)}")
        
        return None
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and log.
        
        Args:
            request: FastAPI request
            call_next: Next middleware or endpoint
        
        Returns:
            Response
        """
        # Generate request ID
        request_id = get_request_id(request)
        
        # Store request ID in request state
        request.state.request_id = request_id
        
        # Log request
        await self._log_request(request, request_id)
        
        # Get request body if needed
        request_body = await self._get_request_body(request)
        if request_body:
            logger.debug(f"Request body [{request_id}]: {request_body[:500]}")
        
        # Process request
        start_time = time.time()
        error = None
        response = None
        
        try:
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Log response body if enabled
            if self.log_response_body and hasattr(response, "body"):
                try:
                    body = response.body
                    if body:
                        body_str = body.decode("utf-8")[:500]
                        logger.debug(f"Response body [{request_id}]: {body_str}")
                except Exception:
                    pass
            
            return response
            
        except Exception as e:
            error = e
            raise
        
        finally:
            await self._log_response(request, response, request_id, start_time, error)


# =====================================================
# SIMPLE LOGGING UTILITIES
# =====================================================

class RequestLogger:
    """
    Simple request logger for manual logging inside endpoints.
    """
    
    @staticmethod
    def log_info(request: Request, message: str, **kwargs):
        """Log info message with request context."""
        request_id = get_request_id(request)
        logger.info(json.dumps({
            "request_id": request_id,
            "message": message,
            **kwargs
        }))
    
    @staticmethod
    def log_warning(request: Request, message: str, **kwargs):
        """Log warning message with request context."""
        request_id = get_request_id(request)
        logger.warning(json.dumps({
            "request_id": request_id,
            "message": message,
            **kwargs
        }))
    
    @staticmethod
    def log_error(request: Request, message: str, **kwargs):
        """Log error message with request context."""
        request_id = get_request_id(request)
        logger.error(json.dumps({
            "request_id": request_id,
            "message": message,
            **kwargs
        }))


# =====================================================
# PERFORMANCE LOGGING
# =====================================================

class PerformanceLogger:
    """
    Context manager for measuring and logging operation performance.
    
    Usage:
        with PerformanceLogger(request, "database_query"):
            result = await db.query()
    """
    
    def __init__(self, request: Request, operation: str):
        self.request = request
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        request_id = get_request_id(self.request)
        
        log_data = {
            "request_id": request_id,
            "event": "performance",
            "operation": self.operation,
            "duration_ms": round(duration_ms, 2)
        }
        
        if exc_val:
            log_data["error"] = str(exc_val)
            logger.warning(json.dumps(log_data))
        else:
            logger.debug(json.dumps(log_data))


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("LoggingMiddleware module loaded successfully")
    
    # Test sensitive data masking
    test_data = '{"password":"secret123","email":"test@example.com"}'
    masked = mask_sensitive_data(test_data)
    print(f"\nMasking test:")
    print(f"  Original: {test_data}")
    print(f"  Masked: {masked}")
    
    # Test headers masking
    test_headers = {"Authorization": "Bearer token123", "Content-Type": "application/json"}
    masked_headers = mask_headers(test_headers)
    print(f"\nHeaders masking:")
    print(f"  Original: {test_headers}")
    print(f"  Masked: {masked_headers}")
    
    print("\n✅ LoggingMiddleware ready for integration")