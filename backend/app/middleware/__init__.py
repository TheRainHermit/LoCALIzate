"""
Middleware module for LoCALIzate Backend
=======================================

Custom middleware for request/response processing.

Available Middlewares:
    - AuthMiddleware: JWT authentication and user context injection
    - LoggingMiddleware: Request/response logging with timing
    - RateLimitMiddleware: Rate limiting to prevent abuse

Usage in main.py:
    from app.middleware import AuthMiddleware, LoggingMiddleware, RateLimitMiddleware
    
    # Add middleware (order matters!)
    app.add_middleware(LoggingMiddleware)  # First: log all requests
    app.add_middleware(RateLimitMiddleware)  # Second: rate limiting
    app.add_middleware(AuthMiddleware)  # Last: authentication
"""

from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

__all__ = [
    "AuthMiddleware",
    "LoggingMiddleware",
    "RateLimitMiddleware",
]

__version__ = "1.0.0"

# Middleware descriptions
MIDDLEWARE_DESCRIPTIONS = {
    "AuthMiddleware": "Autenticación JWT y contexto de usuario",
    "LoggingMiddleware": "Logging de requests/responses con timing",
    "RateLimitMiddleware": "Limitación de requests por IP/usuario"
}


def get_middleware_info() -> dict:
    """Get information about available middlewares."""
    return {
        "version": __version__,
        "middlewares": MIDDLEWARE_DESCRIPTIONS,
        "total_middlewares": len(MIDDLEWARE_DESCRIPTIONS)
    }


def list_middlewares() -> list:
    """List all available middleware names."""
    return list(MIDDLEWARE_DESCRIPTIONS.keys())


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Middleware Module - Information")
    print("=" * 50)
    
    info = get_middleware_info()
    print(f"\n📦 Version: {info['version']}")
    print(f"📋 Total middlewares: {info['total_middlewares']}")
    print("\n🔧 Middlewares disponibles:")
    
    for name, description in info['middlewares'].items():
        print(f"   ✓ {name}: {description}")
    
    print("\n✅ Middleware module loaded successfully")