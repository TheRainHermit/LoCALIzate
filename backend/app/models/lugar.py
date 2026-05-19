"""
Lugar Model for LoCALIzate Backend
================================

Model representing tourist places in Cali, Colombia.
Includes attractions like Cristo Rey, El Gato del Río, Iglesia La Ermita,
Río Pance, Zoológico de Cali, and more.

Fields:
    - Basic: id, nombre, slug, descripcion
    - Location: latitud, longitud, direccion, barrio, comuna
    - Categorization: interes (cultura, naturaleza, gastronomia, salsa, aventura)
    - Details: horario, precio, rating, rating_count
    - Media: imagen, imagenes (array)
    - Metadata: tip_caleño, historia, datos_curiosos
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


# =====================================================
# ENUMS
# =====================================================

class InteresType(str, Enum):
    """Types of interests/categories for places."""
    CULTURA = "cultura"
    NATURALEZA = "naturaleza"
    GASTRONOMIA = "gastronomia"
    SALSA = "salsa"
    AVENTURA = "aventura"
    
    @classmethod
    def list_values(cls) -> List[str]:
        return [item.value for item in cls]
    
    @classmethod
    def get_display_name(cls, value: str) -> str:
        """Get display name in Spanish."""
        names = {
            "cultura": "🎭 Cultura",
            "naturaleza": "🌳 Naturaleza",
            "gastronomia": "🍽️ Gastronomía",
            "salsa": "💃 Salsa",
            "aventura": "🧗 Aventura"
        }
        return names.get(value, value)
    
    @classmethod
    def get_icon(cls, value: str) -> str:
        """Get icon for interest type."""
        icons = {
            "cultura": "🎭",
            "naturaleza": "🌳",
            "gastronomia": "🍽️",
            "salsa": "💃",
            "aventura": "🧗"
        }
        return icons.get(value, "📍")


# =====================================================
# BASE MODELS
# =====================================================

class LugarBase(BaseModel):
    """Base model for Lugar with common fields."""
    
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del lugar turístico")
    descripcion: str = Field(..., min_length=10, description="Descripción detallada del lugar")
    descripcion_corta: Optional[str] = Field(None, max_length=300, description="Descripción breve para tarjetas")
    
    # Location
    latitud: float = Field(..., ge=-90, le=90, description="Latitud (coordenada Y)")
    longitud: float = Field(..., ge=-180, le=180, description="Longitud (coordenada X)")
    direccion: Optional[str] = Field(None, max_length=300, description="Dirección física")
    barrio: Optional[str] = Field(None, max_length=100, description="Barrio donde se ubica")
    comuna: Optional[str] = Field(None, max_length=50, description="Comuna de Cali")
    
    # Categorization
    interes: InteresType = Field(..., description="Categoría principal del lugar")
    subcategorias: Optional[List[str]] = Field(None, description="Subcategorías adicionales")
    
    # Details
    horario: Optional[str] = Field(None, max_length=200, description="Horario de atención")
    precio: Optional[str] = Field(None, max_length=100, description="Información de precios")
    precio_min: Optional[int] = Field(None, ge=0, description="Precio mínimo en COP")
    precio_max: Optional[int] = Field(None, ge=0, description="Precio máximo en COP")
    
    # Contact
    telefono: Optional[str] = Field(None, max_length=50, description="Número de teléfono")
    sitio_web: Optional[str] = Field(None, max_length=300, description="Sitio web oficial")
    instagram: Optional[str] = Field(None, max_length=100, description="Instagram oficial")
    email: Optional[str] = Field(None, max_length=200, description="Email de contacto")
    
    # Media
    icono: str = Field(default="📍", max_length=10, description="Emoji/icono representativo")
    imagen: Optional[str] = Field(None, description="URL de la imagen principal")
    imagenes: Optional[List[str]] = Field(None, description="URLs de imágenes adicionales")
    video_url: Optional[str] = Field(None, description="URL de video (tour virtual)")
    
    # Metadata cultural
    tip_caleño: Optional[str] = Field(None, max_length=500, description="Tip o recomendación local")
    historia: Optional[str] = Field(None, description="Historia del lugar")
    datos_curiosos: Optional[List[str]] = Field(None, description="Datos curiosos")
    
    # Status
    destacado: bool = Field(default=False, description="Si es un lugar destacado")
    verificado: bool = Field(default=False, description="Si la información fue verificada")
    activo: bool = Field(default=True, description="Si el lugar está activo en la plataforma")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Cristo Rey",
                "descripcion": "Estatua monumental de 26m con vista panorámica de toda la ciudad",
                "descripcion_corta": "Mirador icónico de Cali",
                "latitud": 3.43587,
                "longitud": -76.56490,
                "direccion": "Cerro de los Cristales, Siloe",
                "barrio": "Siloe",
                "interes": "cultura",
                "horario": "8:00 AM - 6:00 PM",
                "precio": "Gratis",
                "icono": "✝️",
                "tip_caleño": "Ve temprano para evitar el sol fuerte"
            }
        }
    )
    
    @field_validator("latitud")
    @classmethod
    def validate_latitud(cls, v: float) -> float:
        """Validate latitude is within Cali range approximately."""
        # Cali is roughly between 3.2 and 3.6 degrees latitude
        if v < 3.0 or v > 3.7:
            raise ValueError(f"Latitud {v} fuera del rango esperado para Cali (3.0-3.7)")
        return v
    
    @field_validator("longitud")
    @classmethod
    def validate_longitud(cls, v: float) -> float:
        """Validate longitude is within Cali range approximately."""
        # Cali is roughly between -76.7 and -76.4 degrees longitude
        if v < -76.8 or v > -76.3:
            raise ValueError(f"Longitud {v} fuera del rango esperado para Cali (-76.8 a -76.3)")
        return v
    
    @field_validator("precio_min", "precio_max")
    @classmethod
    def validate_precios(cls, v: Optional[int], info) -> Optional[int]:
        """Validate that min price is not greater than max price."""
        if v is not None and v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v
    
    def get_precio_range(self) -> str:
        """Get formatted price range string."""
        if self.precio_min and self.precio_max:
            if self.precio_min == self.precio_max:
                return f"${self.precio_min:,} COP".replace(",", ".")
            return f"${self.precio_min:,} - ${self.precio_max:,} COP".replace(",", ".")
        elif self.precio_min:
            return f"Desde ${self.precio_min:,} COP".replace(",", ".")
        elif self.precio_max:
            return f"Hasta ${self.precio_max:,} COP".replace(",", ".")
        return self.precio or "Consultar"


class LugarCreate(LugarBase):
    """Model for creating a new Lugar."""
    
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    
    @field_validator("slug", mode="before")
    @classmethod
    def generate_slug(cls, v: Optional[str], info) -> str:
        """Generate slug from nombre if not provided."""
        if v:
            return v
        nombre = info.data.get("nombre", "")
        # Generate slug: lowercase, replace spaces with hyphens, remove special chars
        slug = nombre.lower()
        slug = slug.replace(" ", "-")
        slug = slug.replace("á", "a").replace("é", "e").replace("í", "i")
        slug = slug.replace("ó", "o").replace("ú", "u").replace("ü", "u")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        return slug


class LugarUpdate(BaseModel):
    """Model for updating an existing Lugar."""
    
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = None
    descripcion: Optional[str] = Field(None, min_length=10)
    descripcion_corta: Optional[str] = Field(None, max_length=300)
    latitud: Optional[float] = Field(None, ge=-90, le=90)
    longitud: Optional[float] = Field(None, ge=-180, le=180)
    direccion: Optional[str] = Field(None, max_length=300)
    barrio: Optional[str] = Field(None, max_length=100)
    comuna: Optional[str] = Field(None, max_length=50)
    interes: Optional[InteresType] = None
    subcategorias: Optional[List[str]] = None
    horario: Optional[str] = Field(None, max_length=200)
    precio: Optional[str] = Field(None, max_length=100)
    precio_min: Optional[int] = Field(None, ge=0)
    precio_max: Optional[int] = Field(None, ge=0)
    telefono: Optional[str] = Field(None, max_length=50)
    sitio_web: Optional[str] = Field(None, max_length=300)
    instagram: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=200)
    icono: Optional[str] = Field(None, max_length=10)
    imagen: Optional[str] = None
    imagenes: Optional[List[str]] = None
    video_url: Optional[str] = None
    tip_caleño: Optional[str] = Field(None, max_length=500)
    historia: Optional[str] = None
    datos_curiosos: Optional[List[str]] = None
    destacado: Optional[bool] = None
    verificado: Optional[bool] = None
    activo: Optional[bool] = None


# =====================================================
# DATABASE MODEL (for response/DB operations)
# =====================================================

class LugarInDB(LugarBase):
    """Model representing a Lugar as stored in the database."""
    
    id: int = Field(..., description="ID único del lugar")
    slug: str = Field(..., description="Slug URL-friendly")
    rating: float = Field(default=0.0, ge=0, le=5, description="Rating promedio (0-5)")
    rating_count: int = Field(default=0, ge=0, description="Número total de reseñas")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    
    model_config = ConfigDict(from_attributes=True)


class LugarWithRating(LugarInDB):
    """Extended model with rating information."""
    
    rating_stars: str = Field(..., description="Representación visual del rating (★)")
    
    @field_validator("rating_stars", mode="before")
    @classmethod
    def calculate_rating_stars(cls, v: Optional[str], info) -> str:
        """Calculate star representation from rating."""
        rating = info.data.get("rating", 0)
        full_stars = int(rating)
        half_star = rating - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        
        stars = "★" * full_stars
        stars += "½" if half_star else ""
        stars += "☆" * empty_stars
        return stars
    
    def get_rating_percentage(self) -> int:
        """Get rating as percentage (0-100)."""
        return int((self.rating / 5) * 100)


# =====================================================
# FILTERS MODEL
# =====================================================

class LugarFilters(BaseModel):
    """Filters for querying lugares."""
    
    interes: Optional[InteresType] = Field(None, description="Filtrar por categoría")
    busqueda: Optional[str] = Field(None, description="Búsqueda por texto en nombre/descripción")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Rating mínimo")
    max_precio: Optional[int] = Field(None, ge=0, description="Precio máximo")
    destacados: Optional[bool] = Field(None, description="Solo lugares destacados")
    lat: Optional[float] = Field(None, description="Latitud para búsqueda por proximidad")
    lng: Optional[float] = Field(None, description="Longitud para búsqueda por proximidad")
    radio_km: float = Field(default=5.0, ge=0.1, le=50, description="Radio de búsqueda en km")
    limit: int = Field(default=20, ge=1, le=100, description="Límite de resultados")
    offset: int = Field(default=0, ge=0, description="Desplazamiento para paginación")
    
    @property
    def has_location(self) -> bool:
        """Check if location filters are provided."""
        return self.lat is not None and self.lng is not None
    
    @property
    def has_search(self) -> bool:
        """Check if search term is provided."""
        return self.busqueda is not None and len(self.busqueda.strip()) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert filters to dictionary for Supabase query."""
        return {
            k: v for k, v in self.__dict__.items()
            if v is not None and k not in ["lat", "lng", "radio_km", "limit", "offset"]
        }


# =====================================================
# RESPONSE MODELS
# =====================================================

class LugarListResponse(BaseModel):
    """Response model for list of lugares."""
    
    total: int = Field(..., description="Número total de resultados")
    limit: int = Field(..., description="Límite aplicado")
    offset: int = Field(..., description="Desplazamiento aplicado")
    results: List[LugarWithRating] = Field(..., description="Lista de lugares")


class LugarProximityResponse(BaseModel):
    """Response model for proximity search."""
    
    lugar: LugarWithRating
    distancia_km: float = Field(..., description="Distancia desde el punto de referencia")
    tiempo_estimado_min: int = Field(..., description="Tiempo estimado en minutos")
    
    @field_validator("tiempo_estimado_min", mode="before")
    @classmethod
    def calculate_tiempo(cls, v: Optional[int], info) -> int:
        """Calculate estimated time from distance (assuming 30 km/h)."""
        distancia = info.data.get("distancia_km", 0)
        return int((distancia / 30) * 60)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_intereses_list() -> List[Dict[str, str]]:
    """Get list of available interests with display names and icons."""
    return [
        {
            "value": interes.value,
            "label": InteresType.get_display_name(interes.value),
            "icon": InteresType.get_icon(interes.value)
        }
        for interes in InteresType
    ]


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance in kilometers between two points using Haversine formula.
    
    Args:
        lat1, lng1: First point coordinates
        lat2, lng2: Second point coordinates
    
    Returns:
        Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)
    
    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c


# =====================================================
# CONSTANTS
# =====================================================

# Centro de Cali (referencia)
CALI_CENTER_LAT = 3.4516
CALI_CENTER_LNG = -76.5320

# Lista de lugares predefinidos para seeding
PREDEFINED_PLACES = [
    {
        "nombre": "Cristo Rey",
        "latitud": 3.43587,
        "longitud": -76.56490,
        "interes": "cultura",
        "icono": "✝️",
        "rating": 4.7
    },
    {
        "nombre": "El Gato del Río",
        "latitud": 3.45156,
        "longitud": -76.54297,
        "interes": "cultura",
        "icono": "🐱",
        "rating": 4.5
    },
    {
        "nombre": "Iglesia La Ermita",
        "latitud": 3.4520,
        "longitud": -76.53201,
        "interes": "cultura",
        "icono": "⛪",
        "rating": 4.8
    },
    {
        "nombre": "Río Pance",
        "latitud": 3.3325,
        "longitud": -76.6322,
        "interes": "naturaleza",
        "icono": "🏞️",
        "rating": 4.6
    },
    {
        "nombre": "Zoológico de Cali",
        "latitud": 3.4480,
        "longitud": -76.5580,
        "interes": "naturaleza",
        "icono": "🦁",
        "rating": 4.8
    },
    {
        "nombre": "Bulevar del Río",
        "latitud": 3.4533,
        "longitud": -76.5325,
        "interes": "gastronomia",
        "icono": "🌃",
        "rating": 4.6
    }
]


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("Lugar model loaded successfully")
    print(f"Available interests: {InteresType.list_values()}")
    
    # Test example creation
    test_lugar = LugarCreate(
        nombre="Cristo Rey",
        descripcion="Estatua monumental con vista panorámica",
        latitud=3.43587,
        longitud=-76.56490,
        interes="cultura",
        horario="8:00 AM - 6:00 PM"
    )
    print(f"\nTest lugar created: {test_lugar.nombre}")
    print(f"Generated slug: {test_lugar.slug}")
    print(f"Precio range: {test_lugar.get_precio_range()}")
    
    # Test filters
    filters = LugarFilters(interes="cultura", min_rating=4.5)
    print(f"\nFilters: {filters.to_dict()}")
    
    # Test interest display
    print("\nInterests:")
    for interes in get_intereses_list():
        print(f"  {interes['icon']} {interes['label']} ({interes['value']})")