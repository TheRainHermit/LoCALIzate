"""
Usuario Model for LoCALIzate Backend
===================================

Model representing users of the LoCALIzate application.
Integrates with Supabase Auth for authentication and stores
additional profile information and preferences.

Fields:
    - Basic: id, email, nombre, apellido, avatar_url
    - Location: ciudad_origen, pais, latitud, longitud
    - Preferences: intereses, idioma, tema, notificaciones
    - Metrics: total_rutas, total_favoritos, total_resenas
    - Status: activo, verified
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
        """Get display name in Spanish."""
        names = {
            "es": "Español",
            "en": "English"
        }
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
        """Get display name in Spanish."""
        names = {
            "light": "Claro",
            "dark": "Oscuro",
            "system": "Sistema"
        }
        return names.get(value, value)


class InteresType(str, Enum):
    """User interest categories (same as place categories)."""
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
        """Get display name in Spanish."""
        names = {
            "todas": "Todas las notificaciones",
            "solo_eventos": "Solo eventos",
            "solo_promociones": "Solo promociones",
            "ninguna": "Ninguna"
        }
        return names.get(value, value)


# =====================================================
# BASE MODELS
# =====================================================

class UsuarioBase(BaseModel):
    """Base model for Usuario with common fields."""
    
    # Basic information
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del usuario")
    apellido: Optional[str] = Field(None, min_length=1, max_length=100, description="Apellido del usuario")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL del avatar")
    
    # Contact
    telefono: Optional[str] = Field(None, max_length=50, description="Número de teléfono")
    
    # Location
    ciudad_origen: Optional[str] = Field(None, max_length=100, description="Ciudad de origen")
    pais: Optional[str] = Field(None, max_length=100, description="País de origen")
    
    # Current location (for real-time features)
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
    
    @property
    def iniciales(self) -> str:
        """Get user initials for avatar placeholder."""
        iniciales = ""
        if self.nombre and len(self.nombre) > 0:
            iniciales += self.nombre[0].upper()
        if self.apellido and len(self.apellido) > 0:
            iniciales += self.apellido[0].upper()
        return iniciales or "U"
    
    @property
    def tiene_ubicacion(self) -> bool:
        """Check if user has current location set."""
        return self.latitud is not None and self.longitud is not None


class UsuarioCreate(UsuarioBase):
    """Model for creating a new Usuario."""
    
    email: EmailStr = Field(..., description="Email del usuario (usado para autenticación)")
    password: Optional[str] = Field(None, min_length=6, description="Contraseña (opcional con Supabase Auth)")
    
    # Required for first-time creation
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre es requerido al crear")
    
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    
    @field_validator("intereses", mode="before")
    @classmethod
    def validate_intereses(cls, v: Optional[List]) -> Optional[List]:
        """Validate and clean interests list."""
        if v is None:
            return []
        
        # Convert string values to enum if needed
        result = []
        for item in v:
            if isinstance(item, str):
                try:
                    result.append(InteresType(item.lower()))
                except ValueError:
                    # Skip invalid interests
                    continue
            else:
                result.append(item)
        
        # Remove duplicates
        return list(set(result))


class UsuarioUpdate(BaseModel):
    """Model for updating an existing Usuario."""
    
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
# DATABASE MODEL (for response/DB operations)
# =====================================================

class UsuarioInDB(UsuarioBase):
    """Model representing a Usuario as stored in the database."""
    
    id: str = Field(..., description="UUID del usuario (integración con Supabase Auth)")
    email: EmailStr = Field(..., description="Email del usuario")
    
    # Metrics (calculated from other tables)
    total_rutas: int = Field(default=0, ge=0, description="Número total de rutas creadas")
    total_favoritos: int = Field(default=0, ge=0, description="Número total de favoritos")
    total_resenas: int = Field(default=0, ge=0, description="Número total de reseñas escritas")
    
    # Status
    activo: bool = Field(default=True, description="Si la cuenta está activa")
    verified: bool = Field(default=False, description="Si el email está verificado")
    
    # Timestamps
    last_login: Optional[datetime] = Field(None, description="Último inicio de sesión")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    
    model_config = ConfigDict(from_attributes=True)
    
    @property
    def es_turista(self) -> bool:
        """Check if user is likely a tourist (not from Cali)."""
        return self.ciudad_origen != "Cali" if self.ciudad_origen else True
    
    @property
    def es_local(self) -> bool:
        """Check if user is likely a local (from Cali)."""
        return self.ciudad_origen == "Cali" if self.ciudad_origen else False


class UsuarioProfile(UsuarioInDB):
    """Extended user profile with additional computed fields."""
    
    intereses_display: List[Dict[str, str]] = Field(default_factory=list, description="Intereses con nombres e iconos")
    
    @field_validator("intereses_display", mode="before")
    @classmethod
    def compute_intereses_display(cls, v: Optional[List], info) -> List[Dict[str, str]]:
        """Compute display information for interests."""
        intereses = info.data.get("intereses", [])
        result = []
        for interes in intereses:
            if isinstance(interes, str):
                interes_value = interes
            else:
                interes_value = interes.value if hasattr(interes, "value") else str(interes)
            
            result.append({
                "value": interes_value,
                "label": InteresType.get_display_name(interes_value),
                "icon": InteresType.get_icon(interes_value)
            })
        return result
    
    def to_public_profile(self) -> Dict[str, Any]:
        """Get public profile (excludes private information)."""
        return {
            "id": self.id,
            "nombre": self.nombre_completo,
            "avatar_url": self.avatar_url,
            "ciudad_origen": self.ciudad_origen,
            "pais": self.pais,
            "intereses": self.intereses_display,
            "total_rutas": self.total_rutas,
            "total_favoritos": self.total_favoritos,
            "total_resenas": self.total_resenas,
            "created_at": self.created_at
        }


# =====================================================
# USER INTERESTS MODEL (junction table)
# =====================================================

class UsuarioIntereses(BaseModel):
    """Model for user interests junction table."""
    
    usuario_id: str = Field(..., description="ID del usuario")
    interes: InteresType = Field(..., description="Interés del usuario")
    created_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# USER STATISTICS MODEL
# =====================================================

class UsuarioEstadisticas(BaseModel):
    """User statistics and activity metrics."""
    
    usuario_id: str
    total_rutas: int = 0
    total_favoritos: int = 0
    total_resenas: int = 0
    total_lugares_visitados: int = 0
    total_eventos_asistidos: int = 0
    rutas_completadas: int = 0
    dias_activo: int = 0
    
    # Activity breakdown
    intereses_top: List[Dict[str, Any]] = Field(default_factory=list)
    lugares_top: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Badges earned
    badges: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)
    
    @property
    def nivel_explorador(self) -> str:
        """Calculate explorer level based on activity."""
        total = self.total_lugares_visitados
        if total >= 50:
            return "🌎 Explorador Legendario"
        elif total >= 30:
            return "🌟 Explorador Experto"
        elif total >= 15:
            return "⭐ Explorador Avanzado"
        elif total >= 5:
            return "📍 Explorador Activo"
        else:
            return "🚀 Nuevo Explorador"
    
    @property
    def progreso_siguiente_nivel(self) -> int:
        """Calculate progress percentage to next level."""
        total = self.total_lugares_visitados
        if total < 5:
            return int((total / 5) * 100)
        elif total < 15:
            return int(((total - 5) / 10) * 100)
        elif total < 30:
            return int(((total - 15) / 15) * 100)
        elif total < 50:
            return int(((total - 30) / 20) * 100)
        return 100


# =====================================================
# RESPONSE MODELS
# =====================================================

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
    results: List[UsuarioProfile]


# =====================================================
# PREFERENCES MODEL
# =====================================================

class UsuarioPreferencias(BaseModel):
    """User preferences for the application."""
    
    idioma: IdiomaType = IdiomaType.ESPANOL
    tema: TemaType = TemaType.LIGHT
    notificaciones_email: bool = True
    notificaciones_push: bool = True
    notificaciones_tipo: NotificacionType = NotificacionType.TODAS
    compartir_ubicacion: bool = False
    mostrar_en_mapa: bool = True
    recordar_filtros: bool = True
    
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_intereses_default() -> List[InteresType]:
    """Get default interests for new users."""
    return [InteresType.CULTURA, InteresType.GASTRONOMIA]


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


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("Usuario model loaded successfully")
    print(f"Available languages: {IdiomaType.list_values()}")
    print(f"Available themes: {TemaType.list_values()}")
    print(f"Available interests: {InteresType.list_values()}")
    
    # Test example creation
    test_usuario = UsuarioCreate(
        email="juan.perez@example.com",
        nombre="Juan",
        apellido="Pérez",
        ciudad_origen="Cali",
        pais="Colombia",
        intereses=["cultura", "salsa"],
        idioma=IdiomaType.ESPANOL
    )
    print(f"\nTest user created: {test_usuario.email}")
    print(f"Full name: {test_usuario.nombre_completo}")
    print(f"Iniciales: {test_usuario.iniciales}")
    
    # Test full user in DB
    usuario_db = UsuarioInDB(
        id="123e4567-e89b-12d3-a456-426614174000",
        email="juan.perez@example.com",
        nombre="Juan",
        apellido="Pérez",
        ciudad_origen="Cali",
        intereses=["cultura", "salsa"],
        created_at=datetime.now()
    )
    print(f"\nUser in DB: {usuario_db.nombre_completo}")
    print(f"Is local: {usuario_db.es_local}")
    
    # Test available options
    print("\nAvailable interests:")
    for interes in get_intereses_disponibles():
        print(f"  {interes['icon']} {interes['label']} ({interes['value']})")
    
    print("\nAvailable themes:")
    for tema in get_temas_disponibles():
        print(f"  {tema['label']} ({tema['value']})")
    
    # Test badges
    print("\nAvailable badges:")
    for badge_key, badge_info in list(BADGES.items())[:5]:
        print(f"  {badge_info['name']}: {badge_info['description']}")