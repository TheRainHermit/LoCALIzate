"""
AR Model for LoCALIzate Backend
==============================

Models for Augmented Reality (AR) features in the LoCALIzate application.

Features:
    - AR session tracking for users
    - Points of Interest (POI) for AR overlay
    - 3D object placement data
    - Location-based AR triggers
    - AR filter and effect configurations

Fields:
    - ARSession: id, usuario_id, lugar_id, started_at, ended_at, duration_seconds
    - ARPointOfInterest: id, lugar_id, latitud, longitud, ar_trigger_type
    - ARObject: id, lugar_id, model_url, scale, rotation, position_offset
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


# =====================================================
# ENUMS
# =====================================================

class ARTriggerType(str, Enum):
    """Types of triggers for AR experiences."""
    LOCATION = "location"           # GPS-based trigger
    QR_CODE = "qr_code"             # QR code scan trigger
    IMAGE = "image"                 # Image recognition trigger
    BEACON = "beacon"               # Bluetooth beacon trigger
    MANUAL = "manual"               # Manual user trigger
    
    @classmethod
    def list_values(cls) -> List[str]:
        return [item.value for item in cls]
    
    @classmethod
    def get_display_name(cls, value: str) -> str:
        """Get display name in Spanish."""
        names = {
            "location": "📍 Ubicación",
            "qr_code": "📷 Código QR",
            "image": "🖼️ Imagen",
            "beacon": "📡 Beacon",
            "manual": "👆 Manual"
        }
        return names.get(value, value)


class ARObjectType(str, Enum):
    """Types of AR objects that can be displayed."""
    INFO_CARD = "info_card"         # Information card overlay
    3D_MODEL = "3d_model"           # 3D model of landmark
    ANIMATION = "animation"         # Animated character/effect
    NAVIGATION = "navigation"       # AR navigation arrows
    HISTORICAL = "historical"       # Historical reconstruction
    CHARACTER = "character"         # Virtual character (parcero)
    EFFECT = "effect"               # Visual effect/particles
    QUIZ = "quiz"                   # Interactive quiz
    
    @classmethod
    def list_values(cls) -> List[str]:
        return [item.value for item in cls]
    
    @classmethod
    def get_display_name(cls, value: str) -> str:
        """Get display name in Spanish."""
        names = {
            "info_card": "📋 Tarjeta de Información",
            "3d_model": "🎨 Modelo 3D",
            "animation": "🎬 Animación",
            "navigation": "🧭 Navegación",
            "historical": "🏛️ Reconstrucción Histórica",
            "character": "🤖 Personaje Virtual",
            "effect": "✨ Efecto Visual",
            "quiz": "❓ Quiz Interactivo"
        }
        return names.get(value, value)


class ARFilterType(str, Enum):
    """AR filter types for camera effects."""
    NORMAL = "normal"
    VINTAGE = "vintage"
    CALI_SALSA = "cali_salsa"
    ARTISTIC = "artistic"
    HISTORICAL = "historical"
    NIGHT = "night"
    
    @classmethod
    def list_values(cls) -> List[str]:
        return [item.value for item in cls]
    
    @classmethod
    def get_display_name(cls, value: str) -> str:
        """Get display name in Spanish."""
        names = {
            "normal": "Normal",
            "vintage": "📸 Vintage",
            "cali_salsa": "💃 Salsa",
            "artistic": "🎨 Artístico",
            "historical": "🏛️ Histórico",
            "night": "🌙 Nocturno"
        }
        return names.get(value, value)


class ARInteractionType(str, Enum):
    """Types of user interactions with AR content."""
    TAP = "tap"
    LONG_PRESS = "long_press"
    SWIPE = "swipe"
    PINCH = "pinch"
    ROTATE = "rotate"
    VOICE = "voice"
    
    @classmethod
    def list_values(cls) -> List[str]:
        return [item.value for item in cls]


# =====================================================
# AR SESSION MODELS
# =====================================================

class ARSessionBase(BaseModel):
    """Base model for AR Session."""
    
    lugar_id: Optional[int] = Field(None, description="ID del lugar asociado a la sesión AR")
    started_at: datetime = Field(default_factory=datetime.now, description="Inicio de la sesión")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lugar_id": 1,
                "started_at": "2026-06-15T10:30:00"
            }
        }
    )


class ARSessionCreate(ARSessionBase):
    """Model for creating a new AR session."""
    
    usuario_id: Optional[str] = Field(None, description="ID del usuario")


class ARSessionUpdate(BaseModel):
    """Model for updating an AR session."""
    
    ended_at: Optional[datetime] = Field(None, description="Fin de la sesión")
    duration_seconds: Optional[int] = Field(None, ge=0, description="Duración en segundos")
    interactions_count: Optional[int] = Field(None, ge=0, description="Número de interacciones")
    objects_viewed: Optional[List[int]] = Field(None, description="IDs de objetos AR vistos")


class ARSessionInDB(ARSessionBase):
    """Model representing an AR session as stored in database."""
    
    id: int = Field(..., description="ID único de la sesión")
    usuario_id: str = Field(..., description="ID del usuario")
    ended_at: Optional[datetime] = Field(None, description="Fin de la sesión")
    duration_seconds: int = Field(default=0, ge=0, description="Duración en segundos")
    interactions_count: int = Field(default=0, ge=0, description="Número de interacciones")
    objects_viewed: Optional[List[int]] = Field(None, description="IDs de objetos AR vistos")
    created_at: datetime = Field(..., description="Fecha de creación")
    
    model_config = ConfigDict(from_attributes=True)
    
    @property
    def duracion_formateada(self) -> str:
        """Get formatted duration string."""
        if self.duration_seconds == 0:
            return "En curso"
        
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
    
    @property
    def esta_activa(self) -> bool:
        """Check if session is still active (not ended)."""
        return self.ended_at is None


# =====================================================
# AR POINT OF INTEREST MODELS
# =====================================================

class ARPointOfInterestBase(BaseModel):
    """Base model for AR Point of Interest."""
    
    lugar_id: int = Field(..., description="ID del lugar asociado")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del POI")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción del POI")
    
    # Location
    latitud: float = Field(..., ge=-90, le=90, description="Latitud")
    longitud: float = Field(..., ge=-180, le=180, description="Longitud")
    altitud: Optional[float] = Field(None, description="Altitud en metros")
    
    # AR configuration
    ar_trigger_type: ARTriggerType = Field(default=ARTriggerType.LOCATION, description="Tipo de trigger")
    ar_object_type: ARObjectType = Field(default=ARObjectType.INFO_CARD, description="Tipo de objeto AR")
    
    # Visual
    icono: str = Field(default="📍", max_length=10, description="Icono para mostrar")
    color: str = Field(default="#FF6B35", description="Color del marcador")
    
    # Range
    activation_radius_meters: float = Field(default=50.0, ge=5, le=500, description="Radio de activación en metros")
    
    # Content
    titulo_ar: Optional[str] = Field(None, max_length=100, description="Título que se muestra en AR")
    contenido_ar: Optional[str] = Field(None, description="Contenido HTML para mostrar en AR")
    imagen_ar: Optional[str] = Field(None, description="URL de imagen para AR")
    video_url: Optional[str] = Field(None, description="URL de video para AR")
    
    # Status
    activo: bool = Field(default=True, description="Si el POI está activo")
    destacado: bool = Field(default=False, description="Si es un POI destacado")


class ARPointOfInterestCreate(ARPointOfInterestBase):
    """Model for creating an AR Point of Interest."""
    
    created_at: Optional[datetime] = Field(default_factory=datetime.now)


class ARPointOfInterestUpdate(BaseModel):
    """Model for updating an AR Point of Interest."""
    
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    latitud: Optional[float] = Field(None, ge=-90, le=90)
    longitud: Optional[float] = Field(None, ge=-180, le=180)
    altitud: Optional[float] = None
    ar_trigger_type: Optional[ARTriggerType] = None
    ar_object_type: Optional[ARObjectType] = None
    icono: Optional[str] = Field(None, max_length=10)
    color: Optional[str] = None
    activation_radius_meters: Optional[float] = Field(None, ge=5, le=500)
    titulo_ar: Optional[str] = Field(None, max_length=100)
    contenido_ar: Optional[str] = None
    imagen_ar: Optional[str] = None
    video_url: Optional[str] = None
    activo: Optional[bool] = None
    destacado: Optional[bool] = None


class ARPointOfInterestInDB(ARPointOfInterestBase):
    """Model representing an AR POI as stored in database."""
    
    id: int = Field(..., description="ID único del POI")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de actualización")
    
    model_config = ConfigDict(from_attributes=True)
    
    @property
    def coordenadas(self) -> Dict[str, float]:
        """Get coordinates as dictionary."""
        return {
            "lat": self.latitud,
            "lng": self.longitud,
            "alt": self.altitud
        }


class ARPointOfInterestWithDistance(ARPointOfInterestInDB):
    """AR POI with distance from user."""
    
    distancia_metros: float = Field(..., description="Distancia desde el usuario en metros")
    
    @property
    def distancia_formateada(self) -> str:
        """Get formatted distance string."""
        if self.distancia_metros < 1000:
            return f"{int(self.distancia_metros)}m"
        return f"{self.distancia_metros / 1000:.1f}km"


# =====================================================
# AR OBJECT MODELS (3D models, animations)
# =====================================================

class ARObjectBase(BaseModel):
    """Base model for AR Object (3D models, animations)."""
    
    lugar_id: int = Field(..., description="ID del lugar asociado")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del objeto")
    tipo: ARObjectType = Field(..., description="Tipo de objeto AR")
    
    # Model files
    model_url: Optional[str] = Field(None, description="URL del archivo 3D (glTF, USDZ)")
    texture_url: Optional[str] = Field(None, description="URL de la textura")
    animation_url: Optional[str] = Field(None, description="URL de la animación")
    
    # Transform
    scale: float = Field(default=1.0, ge=0.1, le=10, description="Escala del objeto")
    rotation_y: float = Field(default=0.0, description="Rotación en grados alrededor del eje Y")
    position_offset_x: float = Field(default=0.0, description="Offset X en metros")
    position_offset_y: float = Field(default=0.0, description="Offset Y en metros")
    position_offset_z: float = Field(default=0.0, description="Offset Z en metros")
    
    # Visual
    color: str = Field(default="#FFFFFF", description="Color predominante")
    material: Optional[str] = Field(None, description="Tipo de material")
    
    # Interaction
    interactivo: bool = Field(default=True, description="Si el objeto responde a interacciones")
    interacciones_permitidas: Optional[List[ARInteractionType]] = Field(None, description="Interacciones permitidas")
    
    # Status
    activo: bool = Field(default=True, description="Si el objeto está activo")


class ARObjectCreate(ARObjectBase):
    """Model for creating an AR Object."""
    
    created_at: Optional[datetime] = Field(default_factory=datetime.now)


class ARObjectUpdate(BaseModel):
    """Model for updating an AR Object."""
    
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo: Optional[ARObjectType] = None
    model_url: Optional[str] = None
    texture_url: Optional[str] = None
    animation_url: Optional[str] = None
    scale: Optional[float] = Field(None, ge=0.1, le=10)
    rotation_y: Optional[float] = None
    position_offset_x: Optional[float] = None
    position_offset_y: Optional[float] = None
    position_offset_z: Optional[float] = None
    color: Optional[str] = None
    material: Optional[str] = None
    interactivo: Optional[bool] = None
    interacciones_permitidas: Optional[List[ARInteractionType]] = None
    activo: Optional[bool] = None


class ARObjectInDB(ARObjectBase):
    """Model representing an AR Object as stored in database."""
    
    id: int = Field(..., description="ID único del objeto")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de actualización")
    
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# AR LOCATION DATA MODELS
# =====================================================

class ARLocationData(BaseModel):
    """Real-time location data for AR features."""
    
    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)
    altitud: Optional[float] = None
    heading: Optional[float] = Field(None, ge=0, le=360, description="Dirección de la brújula en grados")
    accuracy_meters: Optional[float] = Field(None, description="Precisión de la ubicación en metros")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @property
    def tiene_heading(self) -> bool:
        """Check if heading/direction is available."""
        return self.heading is not None
    
    @property
    def es_precisa(self) -> bool:
        """Check if location is precise (accuracy < 20m)."""
        return self.accuracy_meters is not None and self.accuracy_meters < 20


class ARUserContext(BaseModel):
    """User context for AR features."""
    
    usuario_id: str
    location: ARLocationData
    active_filters: Optional[List[ARFilterType]] = Field(None, description="Filtros AR activos")
    ar_session_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# AR RESPONSE MODELS
# =====================================================

class ARNearbyPOIsResponse(BaseModel):
    """Response model for nearby AR points of interest."""
    
    total: int
    pois: List[ARPointOfInterestWithDistance]
    user_location: ARLocationData


class ARObjectPlacement(BaseModel):
    """Response model for AR object placement."""
    
    object_id: int
    object_name: str
    object_type: ARObjectType
    position: Dict[str, float]  # x, y, z
    rotation: Dict[str, float]  # x, y, z
    scale: float
    model_url: Optional[str]
    animation_url: Optional[str]


class ARSessionStartResponse(BaseModel):
    """Response model for starting an AR session."""
    
    session_id: int
    message: str
    nearby_pois: List[ARPointOfInterestWithDistance]
    available_objects: List[ARObjectInDB]
    suggested_filter: Optional[ARFilterType] = None


class ARInteractionResponse(BaseModel):
    """Response model for AR interaction."""
    
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    trigger_next_action: Optional[str] = None


# =====================================================
# AR CONFIGURATION MODELS
# =====================================================

class ARGlobalConfig(BaseModel):
    """Global AR configuration for the application."""
    
    ar_enabled: bool = True
    default_activation_radius_meters: float = 50.0
    max_pois_to_display: int = 20
    update_interval_ms: int = 1000
    show_compass: bool = True
    show_distance_indicator: bool = True
    haptic_feedback: bool = True
    
    # Filters
    available_filters: List[ARFilterType] = Field(default_factory=lambda: list(ARFilterType))
    default_filter: ARFilterType = ARFilterType.NORMAL


class ARPlaceConfig(BaseModel):
    """AR configuration for a specific place."""
    
    lugar_id: int
    has_ar_experience: bool = False
    ar_experience_type: Optional[str] = None
    welcome_message: Optional[str] = None
    tutorial_url: Optional[str] = None
    required_pois: Optional[List[int]] = Field(None, description="POIs que deben activarse")


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def haversine_distance_metros(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance in meters between two points.
    
    Args:
        lat1, lng1: First point coordinates
        lat2, lng2: Second point coordinates
    
    Returns:
        Distance in meters
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371000  # Earth's radius in meters
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)
    
    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c


def calcular_distancia_pois(pois: List[ARPointOfInterestInDB], lat: float, lng: float) -> List[ARPointOfInterestWithDistance]:
    """Calculate distances from user to each POI."""
    results = []
    for poi in pois:
        distancia = haversine_distance_metros(lat, lng, poi.latitud, poi.longitud)
        results.append(ARPointOfInterestWithDistance(
            **poi.model_dump(),
            distancia_metros=distancia
        ))
    
    # Sort by distance
    return sorted(results, key=lambda x: x.distancia_metros)


# Predefined AR POIs for Cali landmarks
PREDEFINED_AR_POIS = [
    {
        "nombre": "Cristo Rey - Mirador 360",
        "descripcion": "Vista panorámica en AR con información de la ciudad",
        "lugar_id": 1,
        "latitud": 3.43587,
        "longitud": -76.56490,
        "ar_trigger_type": "location",
        "ar_object_type": "info_card",
        "icono": "✝️",
        "titulo_ar": "Cristo Rey",
        "destacado": True
    },
    {
        "nombre": "El Gato del Río - AR Historia",
        "descripcion": "Historia de la escultura y sus 12 gatos",
        "lugar_id": 2,
        "latitud": 3.45156,
        "longitud": -76.54297,
        "ar_trigger_type": "location",
        "ar_object_type": "historical",
        "icono": "🐱",
        "titulo_ar": "El Gato del Río",
        "destacado": True
    },
    {
        "nombre": "Plazoleta Jairo Varela - Salsa AR",
        "descripcion": "Activa la experiencia de salsa con música y baile",
        "lugar_id": 12,
        "latitud": 3.4500,
        "longitud": -76.5330,
        "ar_trigger_type": "location",
        "ar_object_type": "animation",
        "icono": "🎺",
        "titulo_ar": "Homenaje al Grupo Niche",
        "destacado": True
    }
]


def get_predefined_ar_pois() -> List[Dict[str, Any]]:
    """Get predefined AR POIs for Cali."""
    return PREDEFINED_AR_POIS


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("AR model loaded successfully")
    print(f"AR trigger types: {ARTriggerType.list_values()}")
    print(f"AR object types: {ARObjectType.list_values()}")
    print(f"AR filter types: {ARFilterType.list_values()}")
    
    # Test AR Session creation
    test_session = ARSessionCreate(
        lugar_id=1,
        usuario_id="test-user-123"
    )
    print(f"\nTest AR Session: ID {test_session.lugar_id}")
    
    # Test AR POI creation
    test_poi = ARPointOfInterestCreate(
        lugar_id=1,
        nombre="Cristo Rey AR",
        descripcion="Experiencia AR en el mirador",
        latitud=3.43587,
        longitud=-76.56490,
        ar_trigger_type=ARTriggerType.LOCATION,
        ar_object_type=ARObjectType.INFO_CARD
    )
    print(f"Test AR POI: {test_poi.nombre}")
    
    # Test distance calculation
    distancia = haversine_distance_metros(3.4516, -76.5320, 3.43587, -76.56490)
    print(f"\nDistance from center to Cristo Rey: {distancia:.0f}m")
    
    # Test location data
    test_location = ARLocationData(
        latitud=3.4516,
        longitud=-76.5320,
        heading=180,
        accuracy_meters=15
    )
    print(f"Test location: {test_location.latitud}, {test_location.longitud}")
    print(f"Precise: {test_location.es_precisa}")
    
    # Test POI distance calculation
    from app.models.ar import ARPointOfInterestInDB
    
    test_pois = [
        ARPointOfInterestInDB(
            id=1,
            lugar_id=1,
            nombre="Cristo Rey",
            latitud=3.43587,
            longitud=-76.56490,
            ar_trigger_type="location",
            ar_object_type="info_card",
            icono="✝️",
            created_at=datetime.now()
        )
    ]
    
    resultados = calcular_distancia_pois(test_pois, 3.4516, -76.5320)
    if resultados:
        print(f"\nPOI distance: {resultados[0].distancia_formateada}")
    
    print("\n✅ AR model ready")