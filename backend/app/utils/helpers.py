"""
Helpers Utility for LoCALIzate Backend
=====================================

Common helper functions used throughout the application.

Functions:
    - format_distance: Format distance in km/m for display
    - format_duration: Format time duration for display
    - format_price: Format price in Colombian Pesos
    - format_rating_stars: Generate star rating display
    - slugify: Create URL-friendly slug from string
    - generate_request_id: Generate unique request ID
    - get_client_ip: Extract client IP from request
    - truncate_text: Truncate text to max length
    - safe_parse_json: Safely parse JSON string
    - normalize_phone: Normalize phone number format
    - normalize_email: Normalize email address
    - extract_coordinates: Extract lat/lng from place object
    - calculate_age_from_birthdate: Calculate age from birthdate
    - is_valid_date_range: Validate date range
    - get_date_range_from_period: Get date range for period (week, month, year)
"""

import re
import uuid
import hashlib
import json
import logging
from typing import Optional, Tuple, List, Dict, Any, Union
from datetime import datetime, date, timedelta
from math import radians, sin, cos, sqrt, atan2

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


# =====================================================
# FORMATTING FUNCTIONS
# =====================================================

def format_distance(distancia_km: float, use_metric: bool = True) -> str:
    """
    Format distance for user display.
    
    Args:
        distancia_km: Distance in kilometers
        use_metric: Use metric system (km/m) or imperial (mi/ft)
    
    Returns:
        Formatted distance string (e.g., "2.5 km" or "500 m")
    """
    if distancia_km < 0:
        return "0 m" if use_metric else "0 ft"
    
    if use_metric:
        if distancia_km < 0.1:
            return f"{int(distancia_km * 1000)} m"
        elif distancia_km < 1:
            return f"{int(distancia_km * 1000)} m"
        else:
            return f"{distancia_km:.1f} km"
    else:
        # Convert to miles
        distancia_mi = distancia_km * 0.621371
        if distancia_mi < 0.1:
            return f"{int(distancia_mi * 5280)} ft"
        else:
            return f"{distancia_mi:.1f} mi"


def format_duration(minutes: int) -> str:
    """
    Format time duration for user display.
    
    Args:
        minutes: Duration in minutes
    
    Returns:
        Formatted duration string (e.g., "2h 30min" or "45min")
    """
    if minutes < 0:
        return "0 min"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if hours == 0:
        return f"{mins} min"
    elif mins == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {mins}min"


def format_price(
    precio_min: Optional[int] = None,
    precio_max: Optional[int] = None,
    precio_texto: Optional[str] = None,
    currency: str = "COP"
) -> str:
    """
    Format price for user display.
    
    Args:
        precio_min: Minimum price in COP
        precio_max: Maximum price in COP
        precio_texto: Raw price text
        currency: Currency code (COP, USD)
    
    Returns:
        Formatted price string
    """
    if precio_min is not None and precio_max is not None:
        if precio_min == precio_max:
            return f"${precio_min:,} {currency}".replace(",", ".")
        return f"${precio_min:,} - ${precio_max:,} {currency}".replace(",", ".")
    elif precio_min is not None:
        return f"Desde ${precio_min:,} {currency}".replace(",", ".")
    elif precio_max is not None:
        return f"Hasta ${precio_max:,} {currency}".replace(",", ".")
    elif precio_texto:
        return precio_texto
    return "Consultar"


def format_rating_stars(rating: float, max_stars: int = 5) -> str:
    """
    Generate star rating display.
    
    Args:
        rating: Rating value (0-5)
        max_stars: Maximum number of stars
    
    Returns:
        String with star characters (★ and ☆)
    """
    if rating < 0:
        rating = 0
    if rating > max_stars:
        rating = max_stars
    
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    empty_stars = max_stars - full_stars - (1 if half_star else 0)
    
    stars = "★" * full_stars
    stars += "½" if half_star else ""
    stars += "☆" * empty_stars
    
    return stars


def format_rating_percentage(rating: float, max_stars: int = 5) -> int:
    """
    Convert rating to percentage.
    
    Args:
        rating: Rating value (0-5)
        max_stars: Maximum number of stars
    
    Returns:
        Percentage (0-100)
    """
    if rating < 0:
        return 0
    if rating > max_stars:
        return 100
    return int((rating / max_stars) * 100)


# =====================================================
# STRING UTILITIES
# =====================================================

def slugify(text: str, max_length: int = 100) -> str:
    """
    Convert string to URL-friendly slug.
    
    Args:
        text: Input text
        max_length: Maximum length of slug
    
    Returns:
        URL-friendly slug
    """
    if not text:
        return ""
    
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces with hyphens
    slug = slug.replace(" ", "-")
    
    # Remove special characters (keep alphanumeric and hyphens)
    slug = re.sub(r'[^\w\-]', '', slug)
    
    # Replace multiple hyphens with single hyphen
    slug = re.sub(r'-+', '-', slug)
    
    # Trim hyphens from ends
    slug = slug.strip('-')
    
    # Limit length
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    return slug


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        suffix: Suffix to add when truncated
    
    Returns:
        Truncated text
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    # Try to truncate at word boundary
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length // 2:
        truncated = truncated[:last_space]
    
    return truncated + suffix


def generate_request_id() -> str:
    """
    Generate unique request ID for tracing.
    
    Returns:
        Unique request ID (8 characters)
    """
    return str(uuid.uuid4())[:8]


def generate_hash(text: str, algorithm: str = "md5") -> str:
    """
    Generate hash of text.
    
    Args:
        text: Input text
        algorithm: Hash algorithm (md5, sha1, sha256)
    
    Returns:
        Hash string
    """
    text_bytes = text.encode('utf-8')
    
    if algorithm == "md5":
        return hashlib.md5(text_bytes).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(text_bytes).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(text_bytes).hexdigest()
    else:
        return hashlib.md5(text_bytes).hexdigest()


# =====================================================
# REQUEST/CLIENT UTILITIES
# =====================================================

def get_client_ip(request) -> str:
    """
    Extract client IP address from request.
    
    Args:
        request: FastAPI request object
    
    Returns:
        Client IP address
    """
    # Check X-Forwarded-For header (proxied requests)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client
    if request.client:
        return request.client.host
    
    return "unknown"


def get_user_agent(request) -> str:
    """
    Extract User-Agent from request.
    
    Args:
        request: FastAPI request object
    
    Returns:
        User-Agent string
    """
    return request.headers.get("User-Agent", "unknown")


# =====================================================
# JSON UTILITIES
# =====================================================

def safe_parse_json(json_string: str, default: Any = None) -> Any:
    """
    Safely parse JSON string, return default on error.
    
    Args:
        json_string: JSON string to parse
        default: Default value on error
    
    Returns:
        Parsed JSON or default
    """
    if not json_string:
        return default
    
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    Safely convert object to JSON string.
    
    Args:
        obj: Object to convert
        default: Default value on error
    
    Returns:
        JSON string
    """
    try:
        return json.dumps(obj, default=str, ensure_ascii=False)
    except Exception:
        return default


# =====================================================
# DATA NORMALIZATION
# =====================================================

def normalize_phone(phone: str, country_code: str = "57") -> str:
    """
    Normalize phone number to standard format.
    
    Args:
        phone: Raw phone number
        country_code: Country code (default: 57 for Colombia)
    
    Returns:
        Normalized phone number
    """
    if not phone:
        return ""
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Remove leading zeros
    digits = digits.lstrip('0')
    
    # Add country code if not present
    if not digits.startswith(country_code):
        digits = country_code + digits
    
    return digits


def normalize_email(email: str) -> str:
    """
    Normalize email address (lowercase, trim).
    
    Args:
        email: Raw email address
    
    Returns:
        Normalized email
    """
    if not email:
        return ""
    
    return email.lower().strip()


def extract_coordinates(place: Dict[str, Any]) -> Tuple[float, float]:
    """
    Extract latitude and longitude from place object.
    
    Args:
        place: Place dict with lat/latitud and lng/longitud fields
    
    Returns:
        Tuple of (latitude, longitude)
    """
    lat = place.get('lat', place.get('latitud', 0.0))
    lng = place.get('lng', place.get('longitud', 0.0))
    
    return float(lat), float(lng)


# =====================================================
# DATE/TIME UTILITIES
# =====================================================

def calculate_age_from_birthdate(birthdate: date) -> int:
    """
    Calculate age from birthdate.
    
    Args:
        birthdate: Birth date
    
    Returns:
        Age in years
    """
    today = date.today()
    age = today.year - birthdate.year
    
    # Adjust if birthday hasn't occurred yet this year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1
    
    return max(0, age)


def is_valid_date_range(start_date: date, end_date: date) -> bool:
    """
    Check if date range is valid.
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        True if end_date >= start_date
    """
    return end_date >= start_date


def get_date_range_from_period(period: str, reference_date: Optional[date] = None) -> Tuple[date, date]:
    """
    Get date range for a period.
    
    Args:
        period: Period string (today, tomorrow, week, month, year)
        reference_date: Reference date (defaults to today)
    
    Returns:
        Tuple of (start_date, end_date)
    """
    if reference_date is None:
        reference_date = date.today()
    
    if period == "today":
        return reference_date, reference_date
    
    elif period == "tomorrow":
        tomorrow = reference_date + timedelta(days=1)
        return tomorrow, tomorrow
    
    elif period == "week":
        start = reference_date - timedelta(days=reference_date.weekday())
        end = start + timedelta(days=6)
        return start, end
    
    elif period == "month":
        start = reference_date.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = start.replace(month=start.month + 1, day=1) - timedelta(days=1)
        return start, end
    
    elif period == "year":
        start = reference_date.replace(month=1, day=1)
        end = reference_date.replace(month=12, day=31)
        return start, end
    
    else:
        # Default to today
        return reference_date, reference_date


# =====================================================
# DISTANCE CALCULATIONS
# =====================================================

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance in kilometers between two points using Haversine formula.
    
    Args:
        lat1, lng1: First point coordinates
        lat2, lng2: Second point coordinates
    
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)
    
    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c


def calculate_azimuth(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate azimuth (bearing) from point1 to point2 in degrees.
    
    Args:
        lat1, lng1: First point coordinates
        lat2, lng2: Second point coordinates
    
    Returns:
        Azimuth in degrees (0-360, 0 = North)
    """
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lng = radians(lng2 - lng1)
    
    x = sin(delta_lng) * cos(lat2_rad)
    y = cos(lat1_rad) * sin(lat2_rad) - sin(lat1_rad) * cos(lat2_rad) * cos(delta_lng)
    
    azimuth = atan2(x, y)
    azimuth_deg = degrees(azimuth)
    
    return (azimuth_deg + 360) % 360


def calculate_cardinal_direction(azimuth: float) -> str:
    """
    Convert azimuth to cardinal direction (8-point compass).
    
    Args:
        azimuth: Angle in degrees (0-360)
    
    Returns:
        Cardinal direction (N, NE, E, SE, S, SW, W, NW)
    """
    directions = [
        ("N", 0, 22.5),
        ("NE", 22.5, 67.5),
        ("E", 67.5, 112.5),
        ("SE", 112.5, 157.5),
        ("S", 157.5, 202.5),
        ("SW", 202.5, 247.5),
        ("W", 247.5, 292.5),
        ("NW", 292.5, 337.5),
        ("N", 337.5, 360)
    ]
    
    for direction, start, end in directions:
        if start <= azimuth < end:
            return direction
    
    return "N"


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("Helpers utility loaded successfully")
    
    # Test formatting
    print(f"\nFormat distance:")
    print(f"  0.05 km -> {format_distance(0.05)}")
    print(f"  0.5 km -> {format_distance(0.5)}")
    print(f"  2.5 km -> {format_distance(2.5)}")
    
    print(f"\nFormat duration:")
    print(f"  30 min -> {format_duration(30)}")
    print(f"  90 min -> {format_duration(90)}")
    print(f"  150 min -> {format_duration(150)}")
    
    print(f"\nFormat price:")
    print(f"  (10000, 20000) -> {format_price(10000, 20000)}")
    print(f"  (25000, None) -> {format_price(25000)}")
    
    print(f"\nRating stars:")
    print(f"  4.7 -> {format_rating_stars(4.7)}")
    print(f"  3.2 -> {format_rating_stars(3.2)}")
    
    print(f"\nSlugify:")
    print(f"  'Cristo Rey, Cali' -> {slugify('Cristo Rey, Cali')}")
    
    print("\n✅ Helpers utility ready")