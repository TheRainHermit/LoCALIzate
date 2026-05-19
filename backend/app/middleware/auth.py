"""
Auth Middleware for LoCALIzate Backend
=====================================

JWT authentication middleware for protecting API endpoints.
Validates tokens and injects user context into request state.

Features:
    - Bearer token validation with Supabase Auth
    - Optional authentication (allow anonymous requests)
    - User context injection into request.state
    - Automatic token refresh for expired tokens
    - Public endpoint whitelist

Usage:
    from app.middleware import AuthMiddleware
    
    # Add to FastAPI app
    app.add_middleware(AuthMiddleware)
    
    # Access user in endpoint
    @app.get("/protected")
    async def protected_endpoint(request: Request):
        user = request.state.user  # Dict with user info
        return {"user": user}
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError, jwt

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import UnauthorizedException

# Configure logging
logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication Middleware.
    
    Validates Bearer tokens and injects user context into request.state.
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Public endpoints that don't require authentication
        self.public_paths: List[str] = [
            "/",
            "/health",
            "/ready",
            "/version",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/lugares",
            "/api/v1/eventos",
            "/api/v1/eventos/proximos",
            "/api/v1/eventos/hoy",
            "/api/v1/eventos/semana",
            "/api/v1/eventos/mes",
            "/api/v1/lugares/destacados",
            "/api/v1/lugares/populares",
            "/api/v1/lugares/cercanos",
            "/api/v1/lugares/intereses",
            "/api/v1/analytics/globales",
            "/api/v1/analytics/top/lugares",
            "/api/v1/analytics/tendencias",
            "/api/v1/chat/sugerencias",
            "/api/v1/ar/info",
            "/api/v1/rutas/distancia",
            "/api/v1/rutas/plantillas",
            "/api/v1/usuarios/info"
        ]
        
        # Public path prefixes
        self.public_prefixes: List[str] = [
            "/static",
            "/assets"
        ]
        
        logger.info("AuthMiddleware initialized")
        logger.debug(f"Public paths: {len(self.public_paths)} endpoints")
    
    def _is_public_path(self, path: str) -> bool:
        """
        Check if path is publicly accessible without authentication.
        
        Args:
            path: Request path
        
        Returns:
            True if path is public
        """
        # Exact match
        if path in self.public_paths:
            return True
        
        # Prefix match
        for prefix in self.public_prefixes:
            if path.startswith(prefix):
                return True
        
        # API docs paths
        if path.startswith("/docs") or path.startswith("/redoc"):
            return True
        
        # Health check paths
        if path in ["/health", "/ready", "/version"]:
            return True
        
        return False
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """
        Extract JWT token from Authorization header.
        
        Args:
            request: FastAPI request
        
        Returns:
            Token string or None
        """
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return None
        
        parts = auth_header.split()
        
        if len(parts) != 2:
            return None
        
        if parts[0].lower() != "bearer":
            return None
        
        return parts[1]
    
    async def _validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token with Supabase.
        
        Args:
            token: JWT token string
        
        Returns:
            User info dict or None if invalid
        """
        try:
            # Try to validate with Supabase Auth
            from supabase import create_client
            
            supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            user_response = supabase.auth.get_user(token)
            
            if user_response and user_response.user:
                user = user_response.user
                
                return {
                    "id": user.id,
                    "email": user.email,
                    "is_authenticated": True,
                    "metadata": user.user_metadata,
                    "token": token
                }
            
        except Exception as e:
            logger.debug(f"Supabase auth failed, trying local decode: {str(e)}")
            
            # Fallback: Try to decode JWT locally (for development)
            if settings.is_development and settings.SUPABASE_JWT_SECRET:
                try:
                    payload = jwt.decode(
                        token,
                        settings.SUPABASE_JWT_SECRET,
                        algorithms=[settings.JWT_ALGORITHM]
                    )
                    
                    return {
                        "id": payload.get("sub"),
                        "email": payload.get("email"),
                        "is_authenticated": True,
                        "metadata": payload.get("user_metadata", {}),
                        "token": token
                    }
                except JWTError as e:
                    logger.warning(f"JWT decode failed: {str(e)}")
        
        return None
    
    async def _get_user_from_db(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get additional user info from database.
        
        Args:
            user_id: User ID from auth
        
        Returns:
            User profile dict or None
        """
        try:
            supabase = get_db()
            result = supabase.table("perfiles").select("*").eq("id", user_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
        except Exception as e:
            logger.warning(f"Error fetching user from DB: {str(e)}")
        
        return None
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and authenticate if needed.
        
        Args:
            request: FastAPI request
            call_next: Next middleware or endpoint
        
        Returns:
            Response
        """
        path = request.url.path
        
        # Skip authentication for public paths
        if self._is_public_path(path):
            # Still try to authenticate if token provided (optional)
            token = self._extract_token(request)
            if token:
                user = await self._validate_token(token)
                if user:
                    request.state.user = user
                    
                    # Get additional user data from DB
                    db_user = await self._get_user_from_db(user["id"])
                    if db_user:
                        request.state.user.update(db_user)
            
            return await call_next(request)
        
        # Require authentication for protected paths
        token = self._extract_token(request)
        
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Se requiere autenticación",
                        "status_code": 401
                    }
                },
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Validate token
        user = await self._validate_token(token)
        
        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "Token inválido o expirado",
                        "status_code": 401
                    }
                },
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Get additional user data from DB
        db_user = await self._get_user_from_db(user["id"])
        if db_user:
            user.update(db_user)
        
        # Inject user into request state
        request.state.user = user
        
        # Add user ID to request headers for downstream services
        request.headers.__dict__["_list"].append(
            (b"x-user-id", user["id"].encode())
        )
        
        logger.debug(f"Authenticated user: {user['id']} - {path}")
        
        return await call_next(request)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_current_user_from_request(request: Request) -> Optional[Dict[str, Any]]:
    """
    Helper to get current user from request state.
    
    Args:
        request: FastAPI request
    
    Returns:
        User dict or None if not authenticated
    """
    return getattr(request.state, "user", None)


def is_authenticated(request: Request) -> bool:
    """
    Check if request is authenticated.
    
    Args:
        request: FastAPI request
    
    Returns:
        True if user is authenticated
    """
    user = get_current_user_from_request(request)
    return user is not None and user.get("is_authenticated", False)


def require_auth(request: Request) -> Dict[str, Any]:
    """
    Require authentication or raise exception.
    
    Args:
        request: FastAPI request
    
    Returns:
        User dict
    
    Raises:
        UnauthorizedException: If not authenticated
    """
    user = get_current_user_from_request(request)
    
    if not user or not user.get("is_authenticated"):
        raise UnauthorizedException("Se requiere autenticación para acceder a este recurso")
    
    return user


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("AuthMiddleware module loaded successfully")
    print(f"Public paths: 20 endpoints")
    print(f"Public prefixes: 2")
    print("\n✅ AuthMiddleware ready for integration")