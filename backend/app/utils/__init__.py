"""
Utils module for LoCALIzate / CaliGuia Backend
===============================================

Utility functions and helpers for the application.

Available Modules:
    - helpers: Common helper functions (formatting, calculations)
    - validators: Custom validation functions
    - cache: Cache utilities (Redis/memory)
    - logger: Logging configuration

Usage:
    from app.utils import format_distance, format_duration
    from app.utils import validate_email, validate_phone
    from app.utils import get_cache, set_cache
    from app.utils import setup_logging, get_logger
"""

# Helpers
from app.utils.helpers import (
    format_distance,
    format_duration,
    format_price,
    format_rating_stars,
    slugify,
    generate_request_id,
    get_client_ip,
    truncate_text,
    safe_parse_json,
    normalize_phone,
    normalize_email,
    extract_coordinates,
    calculate_age_from_birthdate,
    is_valid_date_range,
    get_date_range_from_period
)

# Validators
from app.utils.validators import (
    validate_email,
    validate_phone,
    validate_coordinates,
    validate_date,
    validate_time,
    validate_url,
    validate_slug,
    validate_rating,
    validate_price_range,
    validate_id_list,
    validate_intereses,
    ValidationError,
    ValidationResult
)

# Cache
from app.utils.cache import (
    CacheBackend,
    MemoryCache,
    RedisCache,
    get_cache,
    set_cache,
    delete_cache,
    clear_cache,
    cached,
    cached_async
)

# Logger
from app.utils.logger import (
    setup_logging,
    get_logger,
    log_request,
    log_performance,
    log_error,
    set_request_context,
    clear_request_context
)

__all__ = [
    # Helpers
    "format_distance",
    "format_duration",
    "format_price",
    "format_rating_stars",
    "slugify",
    "generate_request_id",
    "get_client_ip",
    "truncate_text",
    "safe_parse_json",
    "normalize_phone",
    "normalize_email",
    "extract_coordinates",
    "calculate_age_from_birthdate",
    "is_valid_date_range",
    "get_date_range_from_period",
    
    # Validators
    "validate_email",
    "validate_phone",
    "validate_coordinates",
    "validate_date",
    "validate_time",
    "validate_url",
    "validate_slug",
    "validate_rating",
    "validate_price_range",
    "validate_id_list",
    "validate_intereses",
    "ValidationError",
    "ValidationResult",
    
    # Cache
    "CacheBackend",
    "MemoryCache",
    "RedisCache",
    "get_cache",
    "set_cache",
    "delete_cache",
    "clear_cache",
    "cached",
    "cached_async",
    
    # Logger
    "setup_logging",
    "get_logger",
    "log_request",
    "log_performance",
    "log_error",
    "set_request_context",
    "clear_request_context",
]

__version__ = "1.0.0"

# Module descriptions
UTILS_DESCRIPTIONS = {
    "helpers": "Funciones auxiliares comunes (formato, cálculos, etc.)",
    "validators": "Validadores personalizados para datos de entrada",
    "cache": "Utilidades de caché (Redis/memoria)",
    "logger": "Configuración de logging para la aplicación"
}


def get_utils_info() -> dict:
    """Get information about available utility modules."""
    return {
        "version": __version__,
        "modules": UTILS_DESCRIPTIONS,
        "total_modules": len(UTILS_DESCRIPTIONS)
    }


def list_utils_modules() -> list:
    """List all available utility module names."""
    return list(UTILS_DESCRIPTIONS.keys())


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Utils Module - Information")
    print("=" * 50)
    
    info = get_utils_info()
    print(f"\n📦 Version: {info['version']}")
    print(f"📋 Total modules: {info['total_modules']}")
    print("\n🔧 Utility modules disponibles:")
    
    for name, description in info['modules'].items():
        print(f"   ✓ {name}: {description}")
    
    print("\n✅ Utils module loaded successfully")