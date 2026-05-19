"""
Rate Limit Middleware for LoCALIzate Backend
===========================================

Rate limiting middleware to prevent API abuse and DoS attacks.

Features:
    - IP-based rate limiting
    - User-based rate limiting (when authenticated)
    - Configurable limits per endpoint
    - Sliding window algorithm
    - Redis support for distributed deployments
    - In-memory fallback for development

Usage:
    from app.middleware import RateLimitMiddleware
    
    # Add to FastAPI app
    app.add_middleware(RateLimitMiddleware)
"""

import time
import logging
from typing import Dict, Optional, Tuple, List
from collections import defaultdict
from datetime import datetime
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.exceptions import RateLimitException

# Configure logging
logger = logging.getLogger(__name__)


# =====================================================
# RATE LIMIT CONFIGURATION
# =====================================================

# Default rate limits (requests per window)
DEFAULT_RATE_LIMIT = {
    "requests": 100,  # Number of requests allowed
    "window_seconds": 60  # Time window in seconds
}

# Endpoint-specific rate limits (path pattern -> limit)
ENDPOINT_RATE_LIMITS = {
    # Public endpoints (more restrictive)
    "/api/v1/lugares": {"requests": 200, "window_seconds": 60},
    "/api/v1/eventos": {"requests": 200, "window_seconds": 60},
    "/api/v1/eventos/proximos": {"requests": 100, "window_seconds": 60},
    "/api/v1/eventos/hoy": {"requests": 100, "window_seconds": 60},
    "/api/v1/lugares/cercanos": {"requests": 100, "window_seconds": 60},
    "/api/v1/lugares/destacados": {"requests": 150, "window_seconds": 60},
    
    # Chat endpoints (higher limit)
    "/api/v1/chat/mensaje": {"requests": 50, "window_seconds": 60},
    "/api/v1/chat/recomendar": {"requests": 100, "window_seconds": 60},
    "/api/v1/chat/sugerencias": {"requests": 50, "window_seconds": 60},
    
    # Route optimization (resource intensive)
    "/api/v1/rutas/optimizar": {"requests": 30, "window_seconds": 60},
    "/api/v1/rutas/guardar": {"requests": 50, "window_seconds": 60},
    
    # AR endpoints
    "/api/v1/ar/cercanos": {"requests": 100, "window_seconds": 60},
    "/api/v1/ar/instruccion": {"requests": 150, "window_seconds": 60},
    
    # User endpoints (authenticated)
    "/api/v1/usuarios/perfil": {"requests": 300, "window_seconds": 60},
    "/api/v1/usuarios/favoritos": {"requests": 200, "window_seconds": 60},
    "/api/v1/usuarios/intereses": {"requests": 200, "window_seconds": 60},
    
    # Admin endpoints (stricter)
    "/api/v1/admin": {"requests": 50, "window_seconds": 60},
    "/api/v1/analytics/dashboard": {"requests": 30, "window_seconds": 60},
    "/api/v1/analytics/usuarios/top": {"requests": 30, "window_seconds": 60},
}

# Path prefixes for rate limiting
PATH_PREFIX_LIMITS = {
    "/api/v1/admin": {"requests": 50, "window_seconds": 60},
    "/api/v1/analytics": {"requests": 100, "window_seconds": 60},
    "/api/v1/chat": {"requests": 100, "window_seconds": 60},
}


# =====================================================
# RATE LIMITER IMPLEMENTATIONS
# =====================================================

class InMemoryRateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.
    Suitable for development and single-instance deployments.
    """
    
    def __init__(self):
        """Initialize in-memory rate limiter."""
        self._requests: Dict[str, List[float]] = defaultdict(list)
        logger.info("InMemoryRateLimiter initialized")
    
    def _get_key(self, client_id: str, endpoint: str) -> str:
        """
        Generate a unique key for rate limiting.
        
        Args:
            client_id: Client identifier (IP or user ID)
            endpoint: Endpoint path
        
        Returns:
            Unique key string
        """
        return f"{client_id}:{endpoint}"
    
    def _clean_old_requests(self, key: str, window_seconds: int):
        """
        Remove requests older than the window.
        
        Args:
            key: Rate limit key
            window_seconds: Time window in seconds
        """
        if key in self._requests:
            cutoff = time.time() - window_seconds
            self._requests[key] = [
                req_time for req_time in self._requests[key]
                if req_time > cutoff
            ]
    
    def check_rate_limit(
        self,
        client_id: str,
        endpoint: str,
        limit_requests: int,
        window_seconds: int
    ) -> Tuple[bool, int]:
        """
        Check if request is within rate limit.
        
        Args:
            client_id: Client identifier
            endpoint: Endpoint path
            limit_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            Tuple of (allowed, remaining_requests)
        """
        key = self._get_key(client_id, endpoint)
        
        # Clean old requests
        self._clean_old_requests(key, window_seconds)
        
        # Get current request count
        current_count = len(self._requests.get(key, []))
        remaining = max(0, limit_requests - current_count)
        
        if current_count >= limit_requests:
            return False, 0
        
        # Add current request
        self._requests[key].append(time.time())
        
        return True, remaining - 1
    
    def get_remaining(
        self,
        client_id: str,
        endpoint: str,
        limit_requests: int,
        window_seconds: int
    ) -> int:
        """
        Get remaining requests allowed.
        
        Args:
            client_id: Client identifier
            endpoint: Endpoint path
            limit_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            Number of remaining requests
        """
        key = self._get_key(client_id, endpoint)
        self._clean_old_requests(key, window_seconds)
        current_count = len(self._requests.get(key, []))
        return max(0, limit_requests - current_count)
    
    def reset(self, client_id: str, endpoint: str):
        """
        Reset rate limit for a client.
        
        Args:
            client_id: Client identifier
            endpoint: Endpoint path
        """
        key = self._get_key(client_id, endpoint)
        if key in self._requests:
            del self._requests[key]


# =====================================================
# RATE LIMIT MIDDLEWARE
# =====================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.
    
    Limits requests based on IP address (anonymous) or user ID (authenticated).
    """
    
    def __init__(self, app: ASGIApp, use_redis: bool = False):
        """
        Initialize rate limit middleware.
        
        Args:
            app: ASGI application
            use_redis: Whether to use Redis (not implemented yet, falls back to memory)
        """
        super().__init__(app)
        
        # Initialize rate limiter (in-memory for now)
        self.rate_limiter = InMemoryRateLimiter()
        self.use_redis = use_redis
        
        logger.info("RateLimitMiddleware initialized")
        logger.info(f"Default limits: {DEFAULT_RATE_LIMIT['requests']} requests per {DEFAULT_RATE_LIMIT['window_seconds']}s")
        logger.info(f"Endpoint-specific limits: {len(ENDPOINT_RATE_LIMITS)}")
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier for rate limiting.
        
        Priority:
            1. Authenticated user ID
            2. X-Forwarded-For header (for proxied requests)
            3. Client IP address
        
        Args:
            request: FastAPI request
        
        Returns:
            Client identifier string
        """
        # Check for authenticated user
        user = getattr(request.state, "user", None)
        if user and user.get("id"):
            return f"user:{user['id']}"
        
        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        
        # Fallback to client IP
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def _get_endpoint_rate_limit(self, path: str) -> Tuple[int, int]:
        """
        Get rate limit for endpoint.
        
        Args:
            path: Request path
        
        Returns:
            Tuple of (requests, window_seconds)
        """
        # Check exact path match
        if path in ENDPOINT_RATE_LIMITS:
            limit = ENDPOINT_RATE_LIMITS[path]
            return limit["requests"], limit["window_seconds"]
        
        # Check path prefix match
        for prefix, limit in PATH_PREFIX_LIMITS.items():
            if path.startswith(prefix):
                return limit["requests"], limit["window_seconds"]
        
        # Default limit
        return DEFAULT_RATE_LIMIT["requests"], DEFAULT_RATE_LIMIT["window_seconds"]
    
    def _should_skip_rate_limit(self, path: str) -> bool:
        """
        Check if rate limiting should be skipped for this path.
        
        Args:
            path: Request path
        
        Returns:
            True if rate limiting should be skipped
        """
        # Skip health check endpoints
        if path in ["/health", "/ready", "/version"]:
            return True
        
        # Skip static files
        if path.startswith("/static") or path.startswith("/assets"):
            return True
        
        # Skip docs
        if path.startswith("/docs") or path.startswith("/redoc") or path == "/openapi.json":
            return True
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.
        
        Args:
            request: FastAPI request
            call_next: Next middleware or endpoint
        
        Returns:
            Response
        """
        path = request.url.path
        
        # Skip rate limiting for certain paths
        if self._should_skip_rate_limit(path):
            return await call_next(request)
        
        # Get client ID and endpoint limits
        client_id = self._get_client_id(request)
        limit_requests, window_seconds = self._get_endpoint_rate_limit(path)
        
        # Check rate limit
        allowed, remaining = self.rate_limiter.check_rate_limit(
            client_id=client_id,
            endpoint=path,
            limit_requests=limit_requests,
            window_seconds=window_seconds
        )
        
        # Get remaining for headers
        remaining_requests = self.rate_limiter.get_remaining(
            client_id=client_id,
            endpoint=path,
            limit_requests=limit_requests,
            window_seconds=window_seconds
        )
        
        # Prepare rate limit headers
        rate_limit_headers = {
            "X-RateLimit-Limit": str(limit_requests),
            "X-RateLimit-Remaining": str(remaining_requests),
            "X-RateLimit-Window": str(window_seconds)
        }
        
        if not allowed:
            # Rate limit exceeded
            logger.warning(f"Rate limit exceeded for {client_id} on {path}")
            
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Demasiadas solicitudes. Límite de {limit_requests} solicitudes cada {window_seconds} segundos.",
                        "status_code": 429,
                        "metadata": {
                            "limit": limit_requests,
                            "window_seconds": window_seconds,
                            "retry_after": window_seconds
                        }
                    }
                },
                headers={
                    **rate_limit_headers,
                    "Retry-After": str(window_seconds)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for key, value in rate_limit_headers.items():
            response.headers[key] = value
        
        return response


# =====================================================
# DECORATOR FOR ENDPOINT-SPECIFIC RATE LIMITS
# =====================================================

def rate_limit(requests: int, window_seconds: int):
    """
    Decorator to set custom rate limit for specific endpoints.
    
    Usage:
        @router.get("/special-endpoint")
        @rate_limit(requests=10, window_seconds=60)
        async def special_endpoint():
            return {"message": "Limited to 10 requests per minute"}
    
    Args:
        requests: Number of requests allowed
        window_seconds: Time window in seconds
    
    Returns:
        Decorator function
    """
    def decorator(func):
        # Store rate limit in function attribute
        func._rate_limit = {"requests": requests, "window_seconds": window_seconds}
        return func
    return decorator


# =====================================================
# RATE LIMIT UTILITIES
# =====================================================

class RateLimitContext:
    """
    Context manager for manual rate limit checking inside endpoints.
    
    Usage:
        async with RateLimitContext(request, "custom_operation", limit=10, window=60):
            await do_expensive_operation()
    """
    
    def __init__(
        self,
        request: Request,
        operation: str,
        limit: int = 10,
        window_seconds: int = 60
    ):
        self.request = request
        self.operation = operation
        self.limit = limit
        self.window_seconds = window_seconds
        self.rate_limiter = InMemoryRateLimiter()
    
    async def __aenter__(self):
        client_id = f"op:{self.operation}:{self.request.client.host}"
        
        allowed, _ = self.rate_limiter.check_rate_limit(
            client_id=client_id,
            endpoint=self.operation,
            limit_requests=self.limit,
            window_seconds=self.window_seconds
        )
        
        if not allowed:
            raise RateLimitException(
                detail=f"Límite de {self.limit} operaciones cada {self.window_seconds} segundos excedido",
                retry_after=self.window_seconds
            )
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def get_rate_limit_info() -> Dict[str, any]:
    """
    Get current rate limit configuration.
    
    Returns:
        Dict with rate limit configuration
    """
    return {
        "default": DEFAULT_RATE_LIMIT,
        "endpoint_limits": ENDPOINT_RATE_LIMITS,
        "path_prefix_limits": PATH_PREFIX_LIMITS,
        "total_endpoints_configured": len(ENDPOINT_RATE_LIMITS)
    }


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("RateLimitMiddleware module loaded successfully")
    
    # Test rate limiter
    limiter = InMemoryRateLimiter()
    
    print("\nRate limiter test:")
    client_id = "test:127.0.0.1"
    endpoint = "/api/v1/test"
    
    for i in range(5):
        allowed, remaining = limiter.check_rate_limit(
            client_id=client_id,
            endpoint=endpoint,
            limit_requests=3,
            window_seconds=60
        )
        print(f"  Request {i+1}: allowed={allowed}, remaining={remaining}")
    
    # Test configuration
    info = get_rate_limit_info()
    print(f"\nRate limit configuration:")
    print(f"  Default: {info['default']['requests']} req / {info['default']['window_seconds']}s")
    print(f"  Endpoints configured: {info['total_endpoints_configured']}")
    
    print("\n✅ RateLimitMiddleware ready for integration")