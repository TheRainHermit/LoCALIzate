"""
AR Schemas for LoCALIzate Backend
================================

Pydantic models for Augmented Reality features request/response validation.

Schemas:
    - LugarARResponse: AR place response
    - InstruccionARResponse: AR instruction response
    - PuntoCardinalResponse: Cardinal point response
    - BrújulaARResponse: AR compass response
    - ARCercanosRequest: Nearby places request
    - ARStatsResponse: AR statistics response
    - ARFilterType: AR filter types enum
    - ARObjectType: AR object types enum
    - ARTriggerType: AR trigger types enum
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


# =====================================================
# ENUMS
# =====================================================

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
        names = {
            "normal": "Normal",
            "vintage": "📸 Vintage",
            "cali_salsa": "💃 Salsa",
            "artistic": "🎨 Artístico",
            "historical": "🏛️ Histórico",
            "night": "🌙 Nocturno"
        }
        return names.get(value, value)


class ARObjectType(str, Enum):
    """Types of AR objects that can be displayed."""
    INFO_CARD = "info_card"
    THREE_D_MODEL = "3d_model"
    ANIMATION = "animation"
    NAVIGATION = "navigation"
    HISTORICAL = "historical"
    CHARACTER = "character"
    EFFECT = "effect"
    QUIZ = "quiz"
    
    @classmethod
    def list_values(cls) -> List[str]:
        return [item.value for item in cls]
    
    @classmethod
    def get_display_name(cls, value: str) -> str:
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


class ARTriggerType(str, Enum):
    """Types of triggers for AR experiences."""
    LOCATION = "location"
    QR_CODE = "qr_code"
    IMAGE = "image"
    BEACON = "beacon"
    MANUAL = "manual"
    
    @classmethod
    def list_values(cls) -> List[str]:
        return [item.value for item in cls]
    
    @classmethod
    def get_display_name(cls, value: str) -> str:
        names = {
            "location": "📍 Ubicación",
            "qr_code": "📷 Código QR",
            "image": "🖼️ Imagen",
            "beacon": "📡 Beacon",
            "manual": "👆 Manual"
        }
        return names.get(value, value)


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class LugarARResponse(BaseModel):
    """Response schema for AR place."""
    
    id: int = Field(..., description="ID del lugar")
    nombre: str = Field(..., description="Nombre del lugar")
    lat: float = Field(..., description="Latitud")
    lng: float = Field(..., description="Longitud")
    distancia_km: float = Field(..., description="Distancia en km")
    distancia_formateada: str = Field(..., description="Distancia formateada")
    azimuth: float = Field(..., description="Ángulo respecto al norte (0-360°)")
    descripcion_corta: str = Field(..., description="Descripción breve")
    rating: float = Field(..., description="Calificación (0-5)")
    icono: str = Field(default="📍", description="Icono/emoji")
    horario: Optional[str] = Field(None, description="Horario de atención")
    
    model_config = ConfigDict(from_attributes=True)


class InstruccionARResponse(BaseModel):
    """Response schema for AR instruction."""
    
    id: int = Field(..., description="ID del lugar")
    nombre: str = Field(..., description="Nombre del lugar")
    icono: str = Field(..., description="Icono/emoji")
    distancia_km: float = Field(..., description="Distancia en km")
    distancia_formateada: str = Field(..., description="Distancia formateada")
    direccion: str = Field(..., description="Dirección textual (ej: 'AL FRENTE')")
    direccion_corta: str = Field(..., description="Dirección corta (ej: '↑ FRENTE')")
    angulo_relativo: float = Field(..., description="Ángulo relativo a la cámara")
    azimuth: float = Field(..., description="Ángulo absoluto al norte")
    descripcion: str = Field(..., description="Descripción del lugar")
    rating: float = Field(..., description="Calificación (0-5)")
    rating_stars: str = Field(..., description="Estrellas de calificación")
    imagen_url: Optional[str] = Field(None, description="URL de la imagen")
    horario: Optional[str] = Field(None, description="Horario de atención")


class PuntoCardinalResponse(BaseModel):
    """Response schema for cardinal point in AR compass."""
    
    nombre: str = Field(..., description="Nombre del lugar")
    distancia_km: float = Field(..., description="Distancia en km")
    distancia_formateada: str = Field(..., description="Distancia formateada")
    azimuth: float = Field(..., description="Ángulo en grados")


class BrújulaARResponse(BaseModel):
    """Response schema for AR compass with 8 directions."""
    
    N: List[PuntoCardinalResponse] = Field(default_factory=list, description="Norte")
    NE: List[PuntoCardinalResponse] = Field(default_factory=list, description="Noreste")
    E: List[PuntoCardinalResponse] = Field(default_factory=list, description="Este")
    SE: List[PuntoCardinalResponse] = Field(default_factory=list, description="Sureste")
    S: List[PuntoCardinalResponse] = Field(default_factory=list, description="Sur")
    SW: List[PuntoCardinalResponse] = Field(default_factory=list, description="Suroeste")
    W: List[PuntoCardinalResponse] = Field(default_factory=list, description="Oeste")
    NW: List[PuntoCardinalResponse] = Field(default_factory=list, description="Noroeste")
    
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    centro: Optional[Dict[str, float]] = Field(None, description="Centro de referencia")


# =====================================================
# REQUEST SCHEMAS
# =====================================================

class ARCercanosRequest(BaseModel):
    """Request schema for nearby AR places."""
    
    lat: float = Field(..., ge=-90, le=90, description="Latitud del usuario")
    lng: float = Field(..., ge=-180, le=180, description="Longitud del usuario")
    heading: Optional[float] = Field(None, ge=0, le=360, description="Dirección del teléfono en grados")
    radio_km: float = Field(2.0, ge=0.5, le=10, description="Radio de búsqueda en km")
    max_resultados: int = Field(20, ge=1, le=50, description="Máximo número de resultados")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lat": 3.4516,
                "lng": -76.5320,
                "heading": 90,
                "radio_km": 2.0,
                "max_resultados": 20
            }
        }
    )


# =====================================================
# STATISTICS SCHEMA
# =====================================================

class ARStatsResponse(BaseModel):
    """Response schema for AR statistics."""
    
    total_cerca: int = Field(..., description="Total de lugares en el radio")
    muy_cerca_500m: int = Field(..., description="Lugares a menos de 500m")
    cerca_1km: int = Field(..., description="Lugares a menos de 1km")
    mas_cercano: Optional[Dict[str, Any]] = Field(None, description="Lugar más cercano")
    conteo_por_interes: Dict[str, int] = Field(default_factory=dict)
    radio_busqueda_km: float = Field(..., description="Radio de búsqueda utilizado")


# =====================================================
# AR OBJECT SCHEMAS
# =====================================================

class ARObjectBase(BaseModel):
    """Base schema for AR object."""
    
    nombre: str = Field(..., min_length=1, max_length=100)
    tipo: ARObjectType
    modelo_url: Optional[str] = Field(None, description="URL del modelo 3D")
    textura_url: Optional[str] = Field(None, description="URL de la textura")
    animacion_url: Optional[str] = Field(None, description="URL de la animación")
    escala: float = Field(default=1.0, ge=0.1, le=10)
    rotacion_y: float = Field(default=0.0, description="Rotación en grados")
    offset_x: float = Field(default=0.0, description="Offset X en metros")
    offset_y: float = Field(default=0.0, description="Offset Y en metros")
    offset_z: float = Field(default=0.0, description="Offset Z en metros")
    interactivo: bool = Field(default=True)


class ARObjectResponse(ARObjectBase):
    """Response schema for AR object."""
    
    id: int
    lugar_id: int
    color: str
    created_at: str
    updated_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ARPointOfInterestBase(BaseModel):
    """Base schema for AR point of interest."""
    
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)
    altitud: Optional[float] = Field(None, description="Altitud en metros")
    trigger_type: ARTriggerType = Field(default=ARTriggerType.LOCATION)
    object_type: ARObjectType = Field(default=ARObjectType.INFO_CARD)
    icono: str = Field(default="📍")
    color: str = Field(default="#FF6B35")
    radio_activacion_m: float = Field(default=50.0, ge=5, le=500)
    titulo_ar: Optional[str] = Field(None, max_length=100)
    contenido_ar: Optional[str] = Field(None)
    imagen_ar: Optional[str] = Field(None)
    video_url: Optional[str] = Field(None)
    activo: bool = Field(default=True)
    destacado: bool = Field(default=False)


class ARPointOfInterestResponse(ARPointOfInterestBase):
    """Response schema for AR point of interest."""
    
    id: int
    lugar_id: int
    created_at: str
    updated_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ARPointOfInterestWithDistance(ARPointOfInterestResponse):
    """AR point of interest with distance from user."""
    
    distancia_metros: float = Field(..., description="Distancia en metros")
    distancia_formateada: str = Field(..., description="Distancia formateada")


# =====================================================
# LOCATION DATA SCHEMA
# =====================================================

class ARLocationData(BaseModel):
    """Schema for real-time location data."""
    
    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)
    altitud: Optional[float] = None
    heading: Optional[float] = Field(None, ge=0, le=360, description="Dirección de la brújula")
    accuracy_metros: Optional[float] = Field(None, description="Precisión de la ubicación")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def tiene_heading(self) -> bool:
        return self.heading is not None
    
    @property
    def es_precisa(self) -> bool:
        return self.accuracy_metros is not None and self.accuracy_metros < 20


class ARUserContext(BaseModel):
    """Schema for user context in AR features."""
    
    usuario_id: str
    location: ARLocationData
    active_filters: Optional[List[ARFilterType]] = None
    ar_session_id: Optional[int] = None


# =====================================================
# SESSION SCHEMAS
# =====================================================

class ARSessionBase(BaseModel):
    """Base schema for AR session."""
    
    lugar_id: Optional[int] = None
    started_at: datetime = Field(default_factory=datetime.now)


class ARSessionCreate(ARSessionBase):
    """Schema for creating an AR session."""
    
    usuario_id: Optional[str] = None


class ARSessionUpdate(BaseModel):
    """Schema for updating an AR session."""
    
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = Field(None, ge=0)
    interactions_count: Optional[int] = Field(None, ge=0)
    objects_viewed: Optional[List[int]] = None


class ARSessionResponse(ARSessionBase):
    """Response schema for AR session."""
    
    id: int
    usuario_id: str
    ended_at: Optional[datetime]
    duration_seconds: int
    interactions_count: int
    objects_viewed: Optional[List[int]]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @property
    def duracion_formateada(self) -> str:
        if self.duration_seconds == 0:
            return "En curso"
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
    
    @property
    def esta_activa(self) -> bool:
        return self.ended_at is None


# =====================================================
# CONFIGURATION SCHEMAS
# =====================================================

class ARGlobalConfig(BaseModel):
    """Global AR configuration."""
    
    ar_enabled: bool = True
    default_radio_activacion_m: float = 50.0
    max_pois_display: int = 20
    update_interval_ms: int = 1000
    show_compass: bool = True
    show_distance_indicator: bool = True
    haptic_feedback: bool = True
    available_filters: List[ARFilterType] = Field(default_factory=lambda: list(ARFilterType))
    default_filter: ARFilterType = ARFilterType.NORMAL


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_ar_filters() -> List[Dict[str, str]]:
    """Get list of available AR filters."""
    return [
        {"value": f.value, "label": f.get_display_name(f.value)}
        for f in ARFilterType
    ]


def get_ar_object_types() -> List[Dict[str, str]]:
    """Get list of available AR object types."""
    return [
        {"value": t.value, "label": t.get_display_name(t.value)}
        for t in ARObjectType
    ]


def get_ar_trigger_types() -> List[Dict[str, str]]:
    """Get list of available AR trigger types."""
    return [
        {"value": t.value, "label": t.get_display_name(t.value)}
        for t in ARTriggerType
    ]


def formatear_distancia_ar(distancia_metros: float) -> str:
    """Format distance for AR display."""
    if distancia_metros < 1000:
        return f"{int(distancia_metros)}m"
    return f"{distancia_metros / 1000:.1f}km"


def calcular_angulo_relativo(azimuth: float, heading: float) -> float:
    """Calculate relative angle between azimuth and heading."""
    relativo = (azimuth - heading + 360) % 360
    if relativo > 180:
        relativo = relativo - 360
    return relativo


def obtener_direccion_textual(angulo_relativo: float) -> tuple:
    """Get textual direction from relative angle."""
    if abs(angulo_relativo) < 15:
        return "AL FRENTE", "↑ FRENTE"
    elif angulo_relativo < 0:
        if angulo_relativo > -45:
            return "IZQUIERDA", "← IZQ"
        else:
            return "IZQUIERDA LEJOS", "↙ IZQ"
    else:
        if angulo_relativo < 45:
            return "DERECHA", "→ DER"
        else:
            return "DERECHA LEJOS", "↘ DER"


# =====================================================
# CONSTANTS
# =====================================================

# Predefined AR POIs for Cali landmarks
PREDEFINED_AR_POIS = [
    {
        "nombre": "Cristo Rey - Mirador 360",
        "descripcion": "Vista panorámica en AR con información de la ciudad",
        "lugar_id": 1,
        "latitud": 3.43587,
        "longitud": -76.56490,
        "trigger_type": "location",
        "object_type": "info_card",
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
        "trigger_type": "location",
        "object_type": "historical",
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
        "trigger_type": "location",
        "object_type": "animation",
        "icono": "🎺",
        "titulo_ar": "Homenaje al Grupo Niche",
        "destacado": True
    }
]


def get_predefined_ar_pois() -> List[Dict[str, Any]]:
    """Get predefined AR POIs for Cali."""
    return PREDEFINED_AR_POIS.copy()


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("AR schemas loaded successfully")
    print(f"AR filter types: {ARFilterType.list_values()}")
    print(f"AR object types: {ARObjectType.list_values()}")
    print(f"AR trigger types: {ARTriggerType.list_values()}")
    
    # Test response creation
    test_lugar = LugarARResponse(
        id=1,
        nombre="Cristo Rey",
        lat=3.43587,
        lng=-76.56490,
        distancia_km=2.5,
        distancia_formateada="2.5 km",
        azimuth=180.0,
        descripcion_corta="Mirador icónico",
        rating=4.7,
        icono="✝️"
    )
    print(f"\nTest AR place: {test_lugar.nombre}")
    print(f"  Distance: {test_lugar.distancia_formateada}")
    
    # Test instruction
    test_instruccion = InstruccionARResponse(
        id=1,
        nombre="Cristo Rey",
        icono="✝️",
        distancia_km=2.5,
        distancia_formateada="2.5 km",
        direccion="AL FRENTE",
        direccion_corta="↑ FRENTE",
        angulo_relativo=5.0,
        azimuth=180.0,
        descripcion="Mirador icónico de Cali",
        rating=4.7,
        rating_stars="★★★★½"
    )
    print(f"\nTest instruction: {test_instruccion.direccion}")
    
    # Test filters
    print("\nAvailable AR filters:")
    for f in get_ar_filters():
        print(f"  {f['label']} ({f['value']})")
    
    # Test angle calculation
    angulo = calcular_angulo_relativo(180, 90)
    direccion, _ = obtener_direccion_textual(angulo)
    print(f"\nAngle: {angulo}° -> Direction: {direccion}")
    
    # Test predefined POIs
    print("\nPredefined AR POIs:")
    for poi in get_predefined_ar_pois():
        print(f"  {poi['icono']} {poi['nombre']}")
    
    print("\n✅ AR schemas ready")