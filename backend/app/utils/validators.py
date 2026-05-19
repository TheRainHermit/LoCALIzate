"""
Validators Utility for LoCALIzate / CaliGuia Backend
=====================================================

Custom validation functions for data validation.

Functions:
    - validate_email: Validate email address format
    - validate_phone: Validate phone number format
    - validate_coordinates: Validate latitude/longitude
    - validate_date: Validate date string
    - validate_time: Validate time string (HH:MM)
    - validate_url: Validate URL format
    - validate_slug: Validate slug format
    - validate_rating: Validate rating value (1-5)
    - validate_price_range: Validate price range
    - validate_id_list: Validate list of IDs
    - validate_intereses: Validate user interests
    - ValidationError: Custom validation exception
    - ValidationResult: Validation result dataclass
"""

import re
from typing import Optional, List, Tuple, Any, Union, Dict
from datetime import datetime, date
from dataclasses import dataclass, field
from urllib.parse import urlparse

from app.core.exceptions import ValidationException


# =====================================================
# CUSTOM EXCEPTIONS
# =====================================================

class ValidationError(Exception):
    """
    Excepción personalizada para errores de validación.
    
    Attributes:
        message: Mensaje de error
        errors: Lista de errores detallados
    """
    
    def __init__(self, message: str, errors: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message)
        self.message = message
        self.errors = errors or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para respuesta API."""
        return {
            "error": self.message,
            "details": self.errors
        }


# =====================================================
# VALIDATION RESULT
# =====================================================

@dataclass
class ValidationResult:
    """
    Result of a validation operation.
    
    Attributes:
        is_valid: Whether validation passed
        errors: List of error messages
        normalized_value: Normalized value (if applicable)
    """
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    normalized_value: Any = None
    
    def add_error(self, error: str):
        """Add an error message."""
        self.is_valid = False
        self.errors.append(error)
    
    def raise_if_invalid(self):
        """Raise ValidationException if validation failed."""
        if not self.is_valid:
            raise ValidationException(
                detail="Error de validación",
                errors=[{"message": e} for e in self.errors]
            )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "normalized_value": self.normalized_value
        }


# =====================================================
# EMAIL VALIDATION
# =====================================================

EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)


def validate_email(email: str, required: bool = True) -> ValidationResult:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        required: Whether email is required
    
    Returns:
        ValidationResult with normalized email if valid
    """
    result = ValidationResult()
    
    if not email:
        if required:
            result.add_error("El correo electrónico es requerido")
        return result
    
    email = email.strip().lower()
    
    if not EMAIL_REGEX.match(email):
        result.add_error("Formato de correo electrónico inválido")
    
    if len(email) > 255:
        result.add_error("El correo electrónico es demasiado largo (máx 255 caracteres)")
    
    if result.is_valid:
        result.normalized_value = email
    
    return result


# =====================================================
# PHONE VALIDATION
# =====================================================

PHONE_REGEX = re.compile(r'^[\d\s\+\-\(\)]{7,20}$')


def validate_phone(phone: str, required: bool = False, country_code: str = "57") -> ValidationResult:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        required: Whether phone is required
        country_code: Country code (default: 57 for Colombia)
    
    Returns:
        ValidationResult with normalized phone if valid
    """
    result = ValidationResult()
    
    if not phone:
        if required:
            result.add_error("El número de teléfono es requerido")
        return result
    
    phone = phone.strip()
    
    # Remove spaces and special characters for validation
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    if not PHONE_REGEX.match(cleaned):
        result.add_error("Formato de número de teléfono inválido")
    
    # Check length
    digits = re.sub(r'\D', '', cleaned)
    if len(digits) < 7 or len(digits) > 15:
        result.add_error("El número de teléfono debe tener entre 7 y 15 dígitos")
    
    if result.is_valid:
        # Normalize: remove all non-digits and add country code
        normalized = digits.lstrip('0')
        if not normalized.startswith(country_code):
            normalized = country_code + normalized
        result.normalized_value = normalized
    
    return result


# =====================================================
# COORDINATES VALIDATION
# =====================================================

def validate_coordinates(lat: float, lng: float, required: bool = True) -> ValidationResult:
    """
    Validate latitude and longitude.
    
    Args:
        lat: Latitude value
        lng: Longitude value
        required: Whether coordinates are required
    
    Returns:
        ValidationResult
    """
    result = ValidationResult()
    
    if lat is None or lng is None:
        if required:
            result.add_error("Las coordenadas son requeridas")
        return result
    
    # Validate latitude
    if not isinstance(lat, (int, float)):
        result.add_error("La latitud debe ser un número")
    elif lat < -90 or lat > 90:
        result.add_error(f"Latitud inválida: {lat}. Debe estar entre -90 y 90")
    
    # Validate longitude
    if not isinstance(lng, (int, float)):
        result.add_error("La longitud debe ser un número")
    elif lng < -180 or lng > 180:
        result.add_error(f"Longitud inválida: {lng}. Debe estar entre -180 y 180")
    
    if result.is_valid:
        result.normalized_value = (float(lat), float(lng))
    
    return result


# =====================================================
# DATE AND TIME VALIDATION
# =====================================================

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"]


def validate_date(
    date_str: str,
    required: bool = True,
    min_date: Optional[date] = None,
    max_date: Optional[date] = None
) -> ValidationResult:
    """
    Validate date string.
    
    Args:
        date_str: Date string to validate
        required: Whether date is required
        min_date: Minimum allowed date
        max_date: Maximum allowed date
    
    Returns:
        ValidationResult with date object if valid
    """
    result = ValidationResult()
    
    if not date_str:
        if required:
            result.add_error("La fecha es requerida")
        return result
    
    date_obj = None
    for fmt in DATE_FORMATS:
        try:
            date_obj = datetime.strptime(date_str, fmt).date()
            break
        except ValueError:
            continue
    
    if date_obj is None:
        result.add_error(f"Formato de fecha inválido. Use YYYY-MM-DD, DD/MM/YYYY o YYYY/MM/DD")
    
    if date_obj:
        if min_date and date_obj < min_date:
            result.add_error(f"La fecha no puede ser anterior a {min_date.isoformat()}")
        if max_date and date_obj > max_date:
            result.add_error(f"La fecha no puede ser posterior a {max_date.isoformat()}")
    
    if result.is_valid and date_obj:
        result.normalized_value = date_obj
    
    return result


def validate_time(time_str: str, required: bool = False) -> ValidationResult:
    """
    Validate time string (HH:MM format).
    
    Args:
        time_str: Time string to validate
        required: Whether time is required
    
    Returns:
        ValidationResult
    """
    result = ValidationResult()
    
    if not time_str:
        if required:
            result.add_error("La hora es requerida")
        return result
    
    # Check format HH:MM
    if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', time_str):
        result.add_error("Formato de hora inválido. Use HH:MM (ejemplo: 14:30)")
    
    if result.is_valid:
        result.normalized_value = time_str
    
    return result


# =====================================================
# URL VALIDATION
# =====================================================

def validate_url(url_str: str, required: bool = False, allow_local: bool = False) -> ValidationResult:
    """
    Validate URL format.
    
    Args:
        url_str: URL to validate
        required: Whether URL is required
        allow_local: Allow localhost URLs
    
    Returns:
        ValidationResult with normalized URL if valid
    """
    result = ValidationResult()
    
    if not url_str:
        if required:
            result.add_error("La URL es requerida")
        return result
    
    url_str = url_str.strip()
    
    # Add protocol if missing
    if not url_str.startswith(('http://', 'https://')):
        url_str = 'https://' + url_str
    
    try:
        parsed = urlparse(url_str)
        
        if not parsed.scheme in ['http', 'https']:
            result.add_error("La URL debe usar HTTP o HTTPS")
        
        if not parsed.netloc:
            result.add_error("URL inválida - dominio no encontrado")
        
        if not allow_local and parsed.netloc in ['localhost', '127.0.0.1']:
            result.add_error("URL local no permitida")
        
        if len(url_str) > 2000:
            result.add_error("La URL es demasiado larga (máx 2000 caracteres)")
        
    except Exception:
        result.add_error("URL inválida")
    
    if result.is_valid:
        result.normalized_value = url_str
    
    return result


# =====================================================
# SLUG VALIDATION
# =====================================================

SLUG_REGEX = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def validate_slug(slug: str, required: bool = True, max_length: int = 100) -> ValidationResult:
    """
    Validate slug format.
    
    Args:
        slug: Slug to validate
        required: Whether slug is required
        max_length: Maximum length
    
    Returns:
        ValidationResult
    """
    result = ValidationResult()
    
    if not slug:
        if required:
            result.add_error("El slug es requerido")
        return result
    
    slug = slug.strip().lower()
    
    if not SLUG_REGEX.match(slug):
        result.add_error("Formato de slug inválido. Use solo letras minúsculas, números y guiones")
    
    if len(slug) > max_length:
        result.add_error(f"El slug es demasiado largo (máx {max_length} caracteres)")
    
    if result.is_valid:
        result.normalized_value = slug
    
    return result


# =====================================================
# RATING VALIDATION
# =====================================================

def validate_rating(rating: Union[int, float], required: bool = True) -> ValidationResult:
    """
    Validate rating value (1-5).
    
    Args:
        rating: Rating value
        required: Whether rating is required
    
    Returns:
        ValidationResult
    """
    result = ValidationResult()
    
    if rating is None:
        if required:
            result.add_error("La calificación es requerida")
        return result
    
    try:
        rating_float = float(rating)
    except (TypeError, ValueError):
        result.add_error("La calificación debe ser un número")
        return result
    
    if rating_float < 1 or rating_float > 5:
        result.add_error(f"Calificación inválida: {rating_float}. Debe estar entre 1 y 5")
    
    if result.is_valid:
        result.normalized_value = round(rating_float, 1)
    
    return result


# =====================================================
# PRICE RANGE VALIDATION
# =====================================================

def validate_price_range(
    precio_min: Optional[int],
    precio_max: Optional[int],
    required: bool = False
) -> ValidationResult:
    """
    Validate price range.
    
    Args:
        precio_min: Minimum price
        precio_max: Maximum price
        required: Whether at least one price is required
    
    Returns:
        ValidationResult
    """
    result = ValidationResult()
    
    if precio_min is None and precio_max is None:
        if required:
            result.add_error("Se requiere al menos un valor de precio")
        return result
    
    if precio_min is not None:
        if precio_min < 0:
            result.add_error("El precio mínimo no puede ser negativo")
    
    if precio_max is not None:
        if precio_max < 0:
            result.add_error("El precio máximo no puede ser negativo")
    
    if precio_min is not None and precio_max is not None:
        if precio_min > precio_max:
            result.add_error("El precio mínimo no puede ser mayor que el precio máximo")
    
    if result.is_valid:
        result.normalized_value = (precio_min, precio_max)
    
    return result


# =====================================================
# ID LIST VALIDATION
# =====================================================

def validate_id_list(
    ids: List[Any],
    required: bool = True,
    min_items: int = 1,
    max_items: int = 20,
    allow_duplicates: bool = False
) -> ValidationResult:
    """
    Validate list of IDs.
    
    Args:
        ids: List of IDs to validate
        required: Whether list is required
        min_items: Minimum number of items
        max_items: Maximum number of items
        allow_duplicates: Whether duplicate IDs are allowed
    
    Returns:
        ValidationResult
    """
    result = ValidationResult()
    
    if not ids:
        if required:
            result.add_error("La lista de IDs es requerida")
        return result
    
    if not isinstance(ids, list):
        result.add_error("Los IDs deben ser una lista")
        return result
    
    if len(ids) < min_items:
        result.add_error(f"Se requieren al menos {min_items} elemento(s)")
    
    if len(ids) > max_items:
        result.add_error(f"Máximo {max_items} elemento(s) permitidos")
    
    # Validate each ID is a positive integer
    for i, item in enumerate(ids):
        try:
            id_int = int(item)
            if id_int <= 0:
                result.add_error(f"El ID en posición {i+1} debe ser un número positivo")
        except (TypeError, ValueError):
            result.add_error(f"El ID en posición {i+1} debe ser un número")
    
    # Check for duplicates
    if not allow_duplicates and len(set(ids)) != len(ids):
        result.add_error("No se permiten IDs duplicados")
    
    if result.is_valid:
        result.normalized_value = [int(i) for i in ids]
    
    return result


# =====================================================
# INTERESES VALIDATION
# =====================================================

VALID_INTERESES = {"cultura", "naturaleza", "gastronomia", "salsa", "aventura"}


def validate_intereses(
    intereses: List[str],
    required: bool = False,
    max_items: int = 5
) -> ValidationResult:
    """
    Validate user interests list.
    
    Args:
        intereses: List of interests
        required: Whether list is required
        max_items: Maximum number of interests
    
    Returns:
        ValidationResult with normalized interests
    """
    result = ValidationResult()
    
    if not intereses:
        if required:
            result.add_error("La lista de intereses es requerida")
        return result
    
    if not isinstance(intereses, list):
        result.add_error("Los intereses deben ser una lista")
        return result
    
    if len(intereses) > max_items:
        result.add_error(f"Máximo {max_items} intereses permitidos")
    
    normalized = []
    for interes in intereses:
        if not isinstance(interes, str):
            result.add_error(f"'{interes}' no es un string válido")
            continue
        
        interes_lower = interes.lower().strip()
        if interes_lower not in VALID_INTERESES:
            result.add_error(f"'{interes}' no es un interés válido. Opciones: {', '.join(VALID_INTERESES)}")
        else:
            normalized.append(interes_lower)
    
    # Remove duplicates
    normalized = list(dict.fromkeys(normalized))
    
    if result.is_valid:
        result.normalized_value = normalized
    
    return result


def get_valid_intereses() -> List[str]:
    """Get list of valid interest categories."""
    return list(VALID_INTERESES)


# =====================================================
# COMPOSITE VALIDATION
# =====================================================

def validate_pagination(page: int, page_size: int) -> Tuple[int, int]:
    """
    Validate and normalize pagination parameters.
    
    Args:
        page: Page number (1-indexed)
        page_size: Items per page
    
    Returns:
        Tuple of (normalized_page, normalized_page_size)
    """
    if page is None or page < 1:
        page = 1
    
    if page_size is None or page_size < 1:
        page_size = 20
    elif page_size > 100:
        page_size = 100
    
    return page, page_size


def validate_search_term(search_term: str, min_length: int = 2, max_length: int = 100) -> Optional[str]:
    """
    Validate and normalize search term.
    
    Args:
        search_term: Search term string
        min_length: Minimum length
        max_length: Maximum length
    
    Returns:
        Normalized search term or None if invalid
    """
    if not search_term:
        return None
    
    normalized = search_term.strip()
    
    if len(normalized) < min_length:
        return None
    
    if len(normalized) > max_length:
        normalized = normalized[:max_length]
    
    return normalized


# =====================================================
# EXPORTS
# =====================================================

__all__ = [
    "ValidationError",
    "ValidationResult",
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
    "get_valid_intereses",
    "validate_pagination",
    "validate_search_term",
]


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Validators utility loaded successfully")
    print("=" * 50)
    
    # Test ValidationError
    print("\n📋 Testing ValidationError:")
    try:
        raise ValidationError("Error de prueba", [{"field": "email", "message": "Formato inválido"}])
    except ValidationError as e:
        print(f"   Error capturado: {e.message}")
        print(f"   Detalles: {e.errors}")
    
    # Test email validation
    print("\n📧 Email validation:")
    print(f"   'test@example.com' -> {validate_email('test@example.com').is_valid}")
    print(f"   'invalid-email' -> {validate_email('invalid-email').is_valid}")
    
    # Test coordinates validation
    print("\n🗺️ Coordinates validation:")
    print(f"   (3.4516, -76.5320) -> {validate_coordinates(3.4516, -76.5320).is_valid}")
    print(f"   (100, 200) -> {validate_coordinates(100, 200).is_valid}")
    
    # Test rating validation
    print("\n⭐ Rating validation:")
    print(f"   4.5 -> {validate_rating(4.5).is_valid}")
    print(f"   6 -> {validate_rating(6).is_valid}")
    
    # Test interests validation
    print("\n🎯 Interests validation:")
    intereses = ["cultura", "salsa", "invalido"]
    result = validate_intereses(intereses)
    print(f"   {intereses} -> valid: {result.is_valid}, errors: {result.errors}")
    
    print("\n✅ Validators utility ready")