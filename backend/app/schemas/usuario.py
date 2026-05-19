"""
Usuario Schemas for LoCALIzate Backend
=====================================

Pydantic models for user profiles, preferences, and favorites request/response validation.

Schemas:
    - UsuarioBase: Base fields for usuario
    - UsuarioCreate: Creation request
    - UsuarioUpdate: Update request
    - UsuarioResponse: Basic response
    - UsuarioProfile: Extended profile response
    - UsuarioPreferences: User preferences
    - UsuarioPreferencesUpdate: Preferences update request
    - UsuarioInteresesUpdate: Interests update request
    - UsuarioStatsResponse: User statistics response
    - FavoritoResponse: Favorite place response
    - IdiomaType, TemaType, NotificacionType: Enums for preferences
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict


# =====================================================
# ENUMS
# =====================================================

class IdiomaType(str, Enum):
    """Supported languages for the application."""
    ESPANOL = "es"
    INGLES = "en"
    
    @classmethod
    def list_values(cls) -> List[str]:
        return [item.value for item in cls]
    
    @classmethod
    def get_display_name(cls, value: str) -> str:
        names = {"es": "Español", "en": "English"}
        return names.get(value, value)


class TemaType(str, Enum):
    """Theme options for the application."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"
    
    @classmethod
    def list_values(cls) -> List[str]:
        return [item.value for item in cls]
    
    @classmethod
    def get_display_name(cls, value: str) -> str:
        names = {"light": "Claro", "dark": "Oscuro", "system": "Sistema"}
        return names.get(value, value)


class NotificacionType(str, Enum):
    """Types of notifications a user can receive."""
    TODAS = "todas"
    SOLO_EVENTOS = "solo_eventos"
    SOLO_PROMOCIONES = "solo_promociones"
    NINGUNA = "ninguna"
    
    @classmethod
    def list_values(cls) -> List[str]:
        return [item.value for item in cls]
    
    @classmethod
    def get_display_name(cls, value: str) -> str:
        names = {
            "todas": "Todas las notificaciones",
            "solo_eventos": "Solo eventos",
            "solo_promociones": "Solo promociones",
            "ninguna": "Ninguna"
        }
        return names.get(value, value)


class InteresType(str, Enum):
    """User interest categories."""
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
        names = {
            "cultura": "🎭 Cultura",
            "naturaleza": "🌳 Naturaleza",
            "gastronomia": "🍽️ Gastronomía",
            "salsa": "💃 Salsa",
            "aventura": "🧗 Aventura"
        }
        return names.get(value, value)


# =====================================================
# BASE SCHEMAS
# =====================================================

class UsuarioBase(BaseModel):
    """Base schema with common fields for usuario."""
    
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del usuario")
    apellido: Optional[str] = Field(None, min_length=1, max_length=100, description="Apellido del usuario")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL del avatar")
    telefono: Optional[str] = Field(None, max_length=50, description="Número de teléfono")
    ciudad_origen: Optional[str] = Field(None, max_length=100, description="Ciudad de origen")
    pais: Optional[str] = Field(None, max_length=100, description="País de origen")
    
    # Current location
    latitud: Optional[float] = Field(None, ge=-90, le=90, description="Latitud actual")
    longitud: Optional[float] = Field(None, ge=-180, le=180, description="Longitud actual")
    
    # Preferences
    intereses: Optional[List[InteresType]] = Field(None, description="Lista de intereses del usuario")
    idioma: IdiomaType = Field(default=IdiomaType.ESPANOL, description="Idioma preferido")
    tema: TemaType = Field(default=TemaType.LIGHT, description="Tema de la interfaz")
    
    # Notification preferences
    notificaciones_email: bool = Field(default=True, description="Recibir notificaciones por email")
    notificaciones_push: bool = Field(default=True, description="Recibir notificaciones push")
    notificaciones_tipo: NotificacionType = Field(
        default=NotificacionType.TODAS,
        description="Tipo de notificaciones a recibir"
    )
    
    # Privacy
    perfil_publico: bool = Field(default=True, description="Si el perfil es público")
    compartir_ubicacion: bool = Field(default=False, description="Si comparte ubicación en tiempo real")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Juan",
                "apellido": "Pérez",
                "ciudad_origen": "Cali",
                "pais": "Colombia",
                "intereses": ["cultura", "salsa", "gastronomia"],
                "idioma": "es",
                "tema": "light"
            }
        }
    )
    
    @property
    def nombre_completo(self) -> str:
        """Get full name of the user."""
        if self.nombre and self.apellido:
            return f"{self.nombre} {self.apellido}"
        return self.nombre or "Turista"


class UsuarioCreate(UsuarioBase):
    """Schema for creating a new usuario."""
    
    email: EmailStr = Field(..., description="Email del usuario")
    password: Optional[str] = Field(None, min_length=6, description="Contraseña")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre requerido")
    
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    
    @field_validator("intereses", mode="before")
    @classmethod
    def validate_intereses(cls, v: Optional[List]) -> Optional[List]:
        """Validate and clean interests list."""
        if v is None:
            return []
        result = []
        for item in v:
            if isinstance(item, str):
                try:
                    result.append(InteresType(item.lower()))
                except ValueError:
                    continue
            else:
                result.append(item)
        return list(set(result))


class UsuarioUpdate(BaseModel):
    """Schema for updating an existing usuario."""
    
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    telefono: Optional[str] = Field(None, max_length=50)
    ciudad_origen: Optional[str] = Field(None, max_length=100)
    pais: Optional[str] = Field(None, max_length=100)
    latitud: Optional[float] = Field(None, ge=-90, le=90)
    longitud: Optional[float] = Field(None, ge=-180, le=180)
    intereses: Optional[List[InteresType]] = None
    idioma: Optional[IdiomaType] = None
    tema: Optional[TemaType] = None
    notificaciones_email: Optional[bool] = None
    notificaciones_push: Optional[bool] = None
    notificaciones_tipo: Optional[NotificacionType] = None
    perfil_publico: Optional[bool] = None
    compartir_ubicacion: Optional[bool] = None


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class UsuarioResponse(BaseModel):
    """Basic response schema for usuario."""
    
    id: str
    email: str
    nombre: Optional[str]
    apellido: Optional[str]
    nombre_completo: str
    avatar_url: Optional[str]
    ciudad_origen: Optional[str]
    pais: Optional[str]
    intereses: List[str]
    created_at: str
    
    model_config = ConfigDict(from_attributes=True)


class UsuarioProfile(UsuarioResponse):
    """Extended profile response with additional fields."""
    
    telefono: Optional[str]
    idioma: str
    tema: str
    notificaciones_email: bool
    notificaciones_push: bool
    perfil_publico: bool
    total_rutas: int = 0
    total_favoritos: int = 0
    total_resenas: int = 0
    last_login: Optional[str] = None
    
    intereses_display: List[Dict[str, str]] = Field(default_factory=list)
    
    @field_validator("intereses_display", mode="before")
    @classmethod
    def compute_intereses_display(cls, v: Optional[List], info) -> List[Dict[str, str]]:
        """Compute display information for interests."""
        intereses = info.data.get("intereses", [])
        result = []
        for interes in intereses:
            interes_value = interes.value if hasattr(interes, "value") else str(interes)
            result.append({
                "value": interes_value,
                "label": InteresType.get_display_name(interes_value),
                "icon": InteresType.get_icon(interes_value)
            })
        return result


class UsuarioPreferences(BaseModel):
    """User preferences schema."""
    
    idioma: IdiomaType = IdiomaType.ESPANOL
    tema: TemaType = TemaType.LIGHT
    notificaciones_email: bool = True
    notificaciones_push: bool = True
    notificaciones_tipo: NotificacionType = NotificacionType.TODAS
    compartir_ubicacion: bool = False
    mostrar_en_mapa: bool = True
    recordar_filtros: bool = True
    
    model_config = ConfigDict(from_attributes=True)


class UsuarioPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    
    idioma: Optional[IdiomaType] = None
    tema: Optional[TemaType] = None
    notificaciones_email: Optional[bool] = None
    notificaciones_push: Optional[bool] = None
    notificaciones_tipo: Optional[NotificacionType] = None
    compartir_ubicacion: Optional[bool] = None
    mostrar_en_mapa: Optional[bool] = None
    recordar_filtros: Optional[bool] = None


class UsuarioInteresesUpdate(BaseModel):
    """Schema for updating user interests."""
    
    intereses: List[InteresType] = Field(..., description="Lista de intereses")
    
    @field_validator("intereses")
    @classmethod
    def validate_intereses(cls, v: List[InteresType]) -> List[InteresType]:
        """Validate interests list."""
        return list(set(v))  # Remove duplicates


class FavoritoResponse(BaseModel):
    """Response schema for favorite place."""
    
    id: int
    nombre: str
    descripcion_corta: Optional[str]
    latitud: float
    longitud: float
    direccion: Optional[str]
    interes: str
    icono: str
    rating: float
    imagen: Optional[str]
    fecha_agregado: str
    
    model_config = ConfigDict(from_attributes=True)


class UsuarioStatsResponse(BaseModel):
    """User statistics response."""
    
    usuario_id: str
    total_rutas: int = 0
    rutas_completadas: int = 0
    tasa_completacion: float = 0.0
    total_favoritos: int = 0
    total_resenas: int = 0
    rating_promedio: float = 0.0
    intereses: List[str] = []
    intereses_count: int = 0
    nivel_explorador: str = "🚀 Nuevo Explorador"
    progreso_siguiente_nivel: int = 0
    badges: List[str] = []


class UsuarioAuthResponse(BaseModel):
    """Response model for authentication operations."""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UsuarioProfile


class UsuarioListResponse(BaseModel):
    """Response model for list of usuarios (admin only)."""
    
    total: int
    limit: int
    offset: int
    results: List[UsuarioResponse]


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_intereses_disponibles() -> List[Dict[str, str]]:
    """Get list of available interests with display info."""
    return [
        {
            "value": interes.value,
            "label": interes.get_display_name(interes.value),
            "icon": interes.get_icon(interes.value)
        }
        for interes in InteresType
    ]


def get_idiomas_disponibles() -> List[Dict[str, str]]:
    """Get list of available languages."""
    return [
        {"value": lang.value, "label": lang.get_display_name(lang.value)}
        for lang in IdiomaType
    ]


def get_temas_disponibles() -> List[Dict[str, str]]:
    """Get list of available themes."""
    return [
        {"value": tema.value, "label": tema.get_display_name(tema.value)}
        for tema in TemaType
    ]


def get_notificaciones_tipos() -> List[Dict[str, str]]:
    """Get list of notification types."""
    return [
        {"value": tipo.value, "label": tipo.get_display_name(tipo.value)}
        for tipo in NotificacionType
    ]


# =====================================================
# CONSTANTS
# =====================================================

# Badges that users can earn
BADGES = {
    "primer_lugar": {"name": "🎯 Primer Lugar", "description": "Visitó su primer lugar turístico"},
    "explorador_5": {"name": "📍 5 Lugares", "description": "Visitó 5 lugares diferentes"},
    "explorador_15": {"name": "⭐ 15 Lugares", "description": "Visitó 15 lugares diferentes"},
    "explorador_30": {"name": "🌟 30 Lugares", "description": "Visitó 30 lugares diferentes"},
    "explorador_50": {"name": "🌎 50 Lugares", "description": "Visitó 50 lugares diferentes"},
    "salsero": {"name": "💃 Salsero", "description": "Visitó 3 lugares de salsa"},
    "foodie": {"name": "🍽️ Foodie", "description": "Visitó 5 restaurantes"},
    "aventurero": {"name": "🧗 Aventurero", "description": "Visitó 3 lugares de aventura"},
    "cultural": {"name": "🎭 Cultural", "description": "Visitó 5 lugares culturales"},
    "ruta_maestra": {"name": "🗺️ Ruta Maestra", "description": "Creó 10 rutas"},
    "festivalero": {"name": "🎉 Festivalero", "description": "Asistió a 3 eventos"},
    "local_experto": {"name": "🏆 Local Experto", "description": "Contribuyó con 10 reseñas"}
}


def get_badges_list() -> Dict[str, Dict[str, str]]:
    """Get all available badges."""
    return BADGES.copy()


def get_intereses_default() -> List[InteresType]:
    """Get default interests for new users."""
    return [InteresType.CULTURA, InteresType.GASTRONOMIA]


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("Usuario schemas loaded successfully")
    print(f"Available languages: {IdiomaType.list_values()}")
    print(f"Available themes: {TemaType.list_values()}")
    print(f"Available interests: {InteresType.list_values()}")
    
    # Test interest display
    print("\nAvailable interests:")
    for interes in get_intereses_disponibles():
        print(f"  {interes['icon']} {interes['label']} ({interes['value']})")
    
    # Test user creation
    test_user = UsuarioCreate(
        email="test@example.com",
        nombre="Test User",
        ciudad_origen="Cali",
        pais="Colombia",
        intereses=["cultura", "salsa"]
    )
    print(f"\nTest user created: {test_user.email}")
    print(f"Full name: {test_user.nombre_completo}")
    
    # Test badges
    print("\nAvailable badges:")
    for key, badge in list(BADGES.items())[:5]:
        print(f"  {badge['name']}: {badge['description']}")
    
    print("\n✅ Usuario schemas ready")