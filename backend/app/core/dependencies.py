"""
Dependencies module for LoCALIzate / CaliGuia Backend
=====================================================

Provides dependency injection functions for FastAPI endpoints.
Includes authentication, database clients, rate limiting, and common utilities.

Usage:
    from app.core.dependencies import get_current_user, get_db, require_admin
    
    @router.get("/perfil")
    async def get_profile(user: dict = Depends(get_current_user)):
        return user
    
    @router.delete("/admin/cleanup")
    async def admin_cleanup(user: dict = Depends(require_admin)):
        # Admin only operation
        pass
"""

import logging
from typing import Optional, Dict, Any, List
from functools import lru_cache
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from jose import JWTError, jwt

from app.core.config import settings
from app.core.database import get_db, get_supabase_admin
from app.core.exceptions import (
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ValidationException
)

# Configure logging
logger = logging.getLogger(__name__)

# Security scheme for Bearer tokens
security = HTTPBearer(auto_error=False)


# =====================================================
# AUTHENTICATION DEPENDENCIES
# =====================================================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase: Client = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the current authenticated user from JWT token.
    
    Returns:
        dict: User information including id, email, and metadata
    
    Raises:
        UnauthorizedException: If token is invalid or missing
    """
    if not credentials:
        raise UnauthorizedException("Token de autenticación requerido")
    
    token = credentials.credentials
    
    try:
        # Verify token with Supabase
        # First try to get user from Supabase Auth
        try:
            user_response = supabase.auth.get_user(token)
            if user_response and user_response.user:
                user_data = user_response.user
                
                # Get additional profile data from perfiles table
                profile_response = supabase.table("perfiles").select("*").eq(
                    "id", user_data.id
                ).execute()
                
                profile = profile_response.data[0] if profile_response.data else {}
                
                return {
                    "id": user_data.id,
                    "email": user_data.email,
                    "nombre": profile.get("nombre", user_data.user_metadata.get("nombre", "Turista")),
                    "apellido": profile.get("apellido", ""),
                    "avatar_url": profile.get("avatar_url", user_data.user_metadata.get("avatar_url")),
                    "intereses": profile.get("intereses", []),
                    "metadata": user_data.user_metadata,
                    "profile": profile
                }
        except Exception as e:
            logger.warning(f"Supabase auth failed, trying JWT decode: {str(e)}")
            
            # Fallback: Try to decode JWT manually (for development)
            if settings.is_development:
                try:
                    payload = jwt.decode(
                        token, 
                        settings.SUPABASE_JWT_SECRET or "dev-secret-key",
                        algorithms=[settings.JWT_ALGORITHM]
                    )
                    return {
                        "id": payload.get("sub"),
                        "email": payload.get("email"),
                        "nombre": payload.get("user_metadata", {}).get("nombre", "Turista"),
                        "metadata": payload.get("user_metadata", {})
                    }
                except JWTError:
                    pass
            
            raise UnauthorizedException("Token inválido o expirado")
            
    except UnauthorizedException:
        raise
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}")
        raise UnauthorizedException(f"Error de autenticación: {str(e)}")


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase: Client = Depends(get_db)
) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, otherwise return None.
    Useful for endpoints that work both with and without authentication.
    """
    try:
        return await get_current_user(credentials, supabase)
    except UnauthorizedException:
        return None


async def require_admin(
    user: Dict[str, Any] = Depends(get_current_user),
    supabase_admin: Client = Depends(get_supabase_admin)
) -> Dict[str, Any]:
    """
    Require admin privileges for an endpoint.
    
    Checks if user has admin role in Supabase.
    """
    try:
        # Check if user has admin role
        # Method 1: Check user metadata
        is_admin = user.get("metadata", {}).get("role") == "admin"
        
        # Method 2: Check in admin_users table (if exists)
        if not is_admin:
            admin_check = supabase_admin.table("admin_users").select("*").eq(
                "user_id", user["id"]
            ).execute()
            is_admin = len(admin_check.data) > 0
        
        if not is_admin:
            raise ForbiddenException("Se requieren permisos de administrador")
        
        return user
    except ForbiddenException:
        raise
    except Exception as e:
        logger.error(f"Error checking admin status: {str(e)}")
        raise ForbiddenException("No se pudo verificar permisos de administrador")


# =====================================================
# DATABASE DEPENDENCIES
# =====================================================

async def get_db_client(
    supabase: Client = Depends(get_db)
) -> Client:
    """
    Get Supabase client for database operations.
    Alias for get_db with async support.
    """
    return supabase


async def get_admin_client(
    supabase_admin: Client = Depends(get_supabase_admin),
    user: Dict[str, Any] = Depends(require_admin)
) -> Client:
    """
    Get admin Supabase client (requires admin privileges).
    """
    return supabase_admin


def get_supabase_client() -> Client:
    """
    Get Supabase client for database operations.
    Alias for get_db for backward compatibility.
    
    Returns:
        Client: Supabase client instance
    """
    from app.core.database import get_db
    return get_db()


# =====================================================
# PAGINATION DEPENDENCIES
# =====================================================

class PaginationParams:
    """Pagination parameters for list endpoints."""
    
    def __init__(
        self,
        page: int = 1,
        limit: int = 20,
        offset: int = 0
    ):
        self.page = max(1, page)
        self.limit = min(100, max(1, limit))
        self.offset = offset if offset > 0 else (self.page - 1) * self.limit
    
    @property
    def skip(self) -> int:
        return self.offset
    
    @property
    def take(self) -> int:
        return self.limit
    
    def to_dict(self) -> dict:
        return {
            "page": self.page,
            "limit": self.limit,
            "offset": self.offset,
            "skip": self.skip,
            "take": self.take
        }


async def get_pagination(
    page: int = 1,
    limit: int = 20,
    offset: int = 0
) -> PaginationParams:
    """
    Dependency for pagination parameters.
    
    Usage:
        @router.get("/lugares")
        async def get_lugares(pagination: PaginationParams = Depends(get_pagination)):
            result = supabase.table("lugares").select("*")\
                .range(pagination.offset, pagination.offset + pagination.limit - 1)\
                .execute()
    """
    return PaginationParams(page=page, limit=limit, offset=offset)


# =====================================================
# FILTER DEPENDENCIES
# =====================================================

class LugarFilters:
    """Filters for lugares endpoints."""
    
    def __init__(
        self,
        categoria: Optional[str] = None,
        interes: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_precio: Optional[int] = None,
        destacado: Optional[bool] = None,
        busqueda: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radio_km: float = 5.0
    ):
        self.categoria = categoria
        self.interes = interes
        self.min_rating = min_rating
        self.max_precio = max_precio
        self.destacado = destacado
        self.busqueda = busqueda
        self.lat = lat
        self.lng = lng
        self.radio_km = radio_km
    
    @property
    def has_location(self) -> bool:
        """Check if location filters are provided."""
        return self.lat is not None and self.lng is not None
    
    @property
    def has_search(self) -> bool:
        """Check if search term is provided."""
        return self.busqueda is not None and len(self.busqueda.strip()) > 0
    
    def to_dict(self) -> dict:
        """Convert filters to dictionary."""
        return {
            k: v for k, v in self.__dict__.items() 
            if v is not None
        }


async def get_lugar_filters(
    categoria: Optional[str] = None,
    interes: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_precio: Optional[int] = None,
    destacado: Optional[bool] = None,
    busqueda: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radio_km: float = 5.0
) -> LugarFilters:
    """
    Dependency for lugar filters.
    """
    return LugarFilters(
        categoria=categoria,
        interes=interes,
        min_rating=min_rating,
        max_precio=max_precio,
        destacado=destacado,
        busqueda=busqueda,
        lat=lat,
        lng=lng,
        radio_km=radio_km
    )


class EventoFilters:
    """Filters for eventos endpoints."""
    
    def __init__(
        self,
        categoria: Optional[str] = None,
        desde: Optional[str] = None,
        hasta: Optional[str] = None,
        destacados: Optional[bool] = None,
        proximos: bool = True
    ):
        self.categoria = categoria
        self.desde = desde
        self.hasta = hasta
        self.destacados = destacados
        self.proximos = proximos


async def get_evento_filters(
    categoria: Optional[str] = None,
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    destacados: Optional[bool] = None,
    proximos: bool = True
) -> EventoFilters:
    """
    Dependency for evento filters.
    """
    return EventoFilters(
        categoria=categoria,
        desde=desde,
        hasta=hasta,
        destacados=destacados,
        proximos=proximos
    )


# =====================================================
# RATE LIMITING DEPENDENCIES
# =====================================================

class RateLimiter:
    """
    Simple in-memory rate limiter.
    For production, use Redis instead.
    """
    
    def __init__(self):
        self._requests: Dict[str, List[datetime]] = {}
    
    def _get_key(self, request: Request, user_id: Optional[str] = None) -> str:
        """Generate a unique key for rate limiting."""
        if user_id:
            return f"user:{user_id}"
        
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def _clean_old_requests(self, key: str, period_seconds: int):
        """Remove requests older than the period."""
        if key in self._requests:
            cutoff = datetime.utcnow() - timedelta(seconds=period_seconds)
            self._requests[key] = [
                req_time for req_time in self._requests[key]
                if req_time > cutoff
            ]
    
    def check_rate_limit(
        self,
        request: Request,
        user_id: Optional[str] = None,
        requests: int = None,
        period: int = None
    ) -> bool:
        """
        Check if request is within rate limit.
        
        Returns:
            bool: True if allowed, False if rate limit exceeded
        """
        if not settings.RATE_LIMIT_ENABLED:
            return True
        
        limit_requests = requests or settings.RATE_LIMIT_REQUESTS
        limit_period = period or settings.RATE_LIMIT_PERIOD
        
        key = self._get_key(request, user_id)
        self._clean_old_requests(key, limit_period)
        
        current_count = len(self._requests.get(key, []))
        
        if current_count >= limit_requests:
            return False
        
        # Add current request
        if key not in self._requests:
            self._requests[key] = []
        self._requests[key].append(datetime.utcnow())
        
        return True
    
    def get_remaining(self, request: Request, user_id: Optional[str] = None) -> int:
        """Get remaining requests allowed."""
        if not settings.RATE_LIMIT_ENABLED:
            return settings.RATE_LIMIT_REQUESTS
        
        key = self._get_key(request, user_id)
        self._clean_old_requests(key, settings.RATE_LIMIT_PERIOD)
        
        current_count = len(self._requests.get(key, []))
        return max(0, settings.RATE_LIMIT_REQUESTS - current_count)


# Global rate limiter instance
_rate_limiter = RateLimiter()


async def check_rate_limit(
    request: Request,
    user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
) -> bool:
    """
    Dependency to check rate limit before processing request.
    
    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    user_id = user.get("id") if user else None
    
    if not _rate_limiter.check_rate_limit(request, user_id):
        remaining = _rate_limiter.get_remaining(request, user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Límite de solicitudes excedido. Intenta de nuevo en unos momentos.",
            headers={"X-RateLimit-Remaining": str(remaining)}
        )
    
    return True


# =====================================================
# REQUEST CONTEXT DEPENDENCIES
# =====================================================

async def get_request_id(request: Request) -> str:
    """
    Get or generate a unique request ID for tracing.
    """
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        import uuid
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
    return request_id


async def get_user_agent(request: Request) -> str:
    """
    Get user agent from request headers.
    """
    return request.headers.get("User-Agent", "unknown")


async def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# =====================================================
# VALIDATION DEPENDENCIES
# =====================================================

async def validate_lugar_id(
    lugar_id: int,
    supabase: Client = Depends(get_db)
) -> Dict[str, Any]:
    """
    Validate that a lugar exists and return it.
    
    Raises:
        NotFoundException: If lugar not found
    """
    result = supabase.table("lugares").select("*").eq("id", lugar_id).execute()
    
    if not result.data:
        raise NotFoundException(f"Lugar con ID {lugar_id} no encontrado")
    
    return result.data[0]


async def validate_evento_id(
    evento_id: int,
    supabase: Client = Depends(get_db)
) -> Dict[str, Any]:
    """
    Validate that an evento exists and return it.
    
    Raises:
        NotFoundException: If evento not found
    """
    result = supabase.table("eventos").select("*").eq("id", evento_id).execute()
    
    if not result.data:
        raise NotFoundException(f"Evento con ID {evento_id} no encontrado")
    
    return result.data[0]


# =====================================================
# COMPOSITE DEPENDENCIES
# =====================================================

async def get_authenticated_db(
    user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_db)
) -> Client:
    """
    Get database client with authenticated user context.
    """
    return supabase


async def get_paginated_lugares(
    pagination: PaginationParams = Depends(get_pagination),
    filters: LugarFilters = Depends(get_lugar_filters)
) -> dict:
    """
    Combined dependency for paginated lugares query.
    """
    return {
        "pagination": pagination,
        "filters": filters
    }


# =====================================================
# TESTING HELPERS
# =====================================================

def reset_rate_limiter():
    """
    Reset rate limiter (useful for testing).
    """
    global _rate_limiter
    _rate_limiter = RateLimiter()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [
    # Auth
    "get_current_user",
    "get_current_user_optional",
    "require_admin",
    
    # Database
    "get_db_client",
    "get_admin_client",
    "get_supabase_client",
    
    # Pagination
    "PaginationParams",
    "get_pagination",
    
    # Filters
    "LugarFilters",
    "get_lugar_filters",
    "EventoFilters",
    "get_evento_filters",
    
    # Rate Limiting
    "check_rate_limit",
    "RateLimiter",
    "reset_rate_limiter",
    
    # Request Context
    "get_request_id",
    "get_user_agent",
    "get_client_ip",
    
    # Validation
    "validate_lugar_id",
    "validate_evento_id",
    
    # Composite
    "get_authenticated_db",
    "get_paginated_lugares",
]


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("Dependencies module loaded successfully")
    print(f"Rate limit enabled: {settings.RATE_LIMIT_ENABLED}")
    print(f"Default rate limit: {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_PERIOD}s")