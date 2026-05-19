"""
Evento Model for LoCALIzate Backend
==================================

Model representing events, festivals, and activities in Cali, Colombia.
Includes major events like:
- Feria de Cali (December 25-30)
- Festival Mundial de Salsa (September)
- Festival Petronio Álvarez (August)
- Salsa al Parque (December)
- Tour Gastronómico del Pacífico (weekly)

Fields:
    - Basic: id, nombre, slug, descripcion
    - Dates: fecha_inicio, fecha_fin, hora_inicio, hora_fin
    - Location: ubicacion, direccion, latitud, longitud
    - Categorization: tags, categoria_id
    - Details: precio, capacidad, destacado
    - Media: imagen, imagenes
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


# =====================================================
# ENUMS
# =====================================================

class EventoFrecuencia(str, Enum):
    """Frequency types for recurring events."""
    UNICO = "unico"
    SEMANAL = "semanal"
    MENSUAL = "mensual"
    ANUAL = "anual"
    
    @classmethod
    def list_values(cls) -> List[str]:
        return [item.value for item in cls]
    
    @classmethod
    def get_display_name(cls, value: str) -> str:
        """Get display name in Spanish."""
        names = {
            "unico": "Único",
            "semanal": "Semanal",
            "mensual": "Mensual",
            "anual": "Anual"
        }
        return names.get(value, value)


class DiaSemana(int, Enum):
    """Days of the week for recurring events (Monday=1 to Sunday=7)."""
    LUNES = 1
    MARTES = 2
    MIERCOLES = 3
    JUEVES = 4
    VIERNES = 5
    SABADO = 6
    DOMINGO = 7
    
    @classmethod
    def get_display_name(cls, value: int) -> str:
        """Get display name in Spanish."""
        names = {
            1: "Lunes",
            2: "Martes",
            3: "Miércoles",
            4: "Jueves",
            5: "Viernes",
            6: "Sábado",
            7: "Domingo"
        }
        return names.get(value, "Desconocido")


# =====================================================
# BASE MODELS
# =====================================================

class EventoBase(BaseModel):
    """Base model for Evento with common fields."""
    
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre del evento")
    descripcion: str = Field(..., min_length=10, description="Descripción detallada del evento")
    descripcion_corta: Optional[str] = Field(None, max_length=300, description="Descripción breve")
    
    # Dates and times
    fecha_inicio: date = Field(..., description="Fecha de inicio del evento")
    fecha_fin: Optional[date] = Field(None, description="Fecha de fin del evento")
    hora_inicio: Optional[str] = Field(None, description="Hora de inicio (formato HH:MM)")
    hora_fin: Optional[str] = Field(None, description="Hora de fin (formato HH:MM)")
    
    # Recurrence
    es_recurrente: bool = Field(default=False, description="Si el evento se repite")
    frecuencia: Optional[EventoFrecuencia] = Field(None, description="Frecuencia de repetición")
    dias_semana: Optional[List[int]] = Field(None, description="Días de la semana (1-7) para eventos semanales")
    
    # Location
    ubicacion: Optional[str] = Field(None, max_length=300, description="Nombre del lugar o espacio")
    direccion: Optional[str] = Field(None, max_length=500, description="Dirección completa")
    lugar_id: Optional[int] = Field(None, description="ID del lugar asociado (tabla lugares)")
    latitud: Optional[float] = Field(None, ge=-90, le=90, description="Latitud para geolocalización")
    longitud: Optional[float] = Field(None, ge=-180, le=180, description="Longitud para geolocalización")
    
    # Details
    precio: Optional[str] = Field(None, max_length=100, description="Información de precios")
    precio_min: Optional[int] = Field(None, ge=0, description="Precio mínimo en COP")
    precio_max: Optional[int] = Field(None, ge=0, description="Precio máximo en COP")
    capacidad: Optional[int] = Field(None, ge=1, description="Capacidad máxima de personas")
    
    # Categorization
    tags: Optional[List[str]] = Field(None, description="Etiquetas para categorización")
    categoria_id: Optional[int] = Field(None, description="ID de categoría (tabla categorias)")
    
    # Media
    icono: str = Field(default="🎉", max_length=10, description="Emoji/icono representativo")
    imagen: Optional[str] = Field(None, description="URL de la imagen principal")
    imagenes: Optional[List[str]] = Field(None, description="URLs de imágenes adicionales")
    video_url: Optional[str] = Field(None, description="URL de video promocional")
    
    # Contact
    organizador: Optional[str] = Field(None, max_length=200, description="Nombre del organizador")
    contacto_email: Optional[str] = Field(None, max_length=200, description="Email de contacto")
    contacto_telefono: Optional[str] = Field(None, max_length=50, description="Teléfono de contacto")
    sitio_web: Optional[str] = Field(None, max_length=300, description="Sitio web del evento")
    instagram: Optional[str] = Field(None, max_length=100, description="Instagram oficial")
    
    # Status
    destacado: bool = Field(default=False, description="Si es un evento destacado")
    activo: bool = Field(default=True, description="Si el evento está activo")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Feria de Cali 2026",
                "descripcion": "La feria más salsera del mundo. Salsódromo, cabalgata y conciertos masivos.",
                "fecha_inicio": "2026-12-25",
                "fecha_fin": "2026-12-30",
                "ubicacion": "Toda la ciudad",
                "precio": "Eventos gratuitos",
                "icono": "🎉",
                "tags": ["Salsa", "Cultura", "Fiesta"]
            }
        }
    )
    
    @field_validator("fecha_inicio", "fecha_fin")
    @classmethod
    def validate_fechas(cls, v: Optional[date], info) -> Optional[date]:
        """Validate dates."""
        if v is None:
            return v
        
        # Check if fecha_fin is after fecha_inicio
        if info.field_name == "fecha_fin" and v is not None:
            fecha_inicio = info.data.get("fecha_inicio")
            if fecha_inicio and v < fecha_inicio:
                raise ValueError("La fecha de fin no puede ser anterior a la fecha de inicio")
        
        return v
    
    @field_validator("hora_inicio", "hora_fin")
    @classmethod
    def validate_horas(cls, v: Optional[str]) -> Optional[str]:
        """Validate time format HH:MM."""
        if v is None:
            return v
        
        import re
        if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError("Formato de hora inválido. Use HH:MM (ejemplo: 14:30)")
        return v
    
    @field_validator("dias_semana")
    @classmethod
    def validate_dias_semana(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """Validate days of week are between 1 and 7."""
        if v is None:
            return v
        
        for dia in v:
            if dia < 1 or dia > 7:
                raise ValueError("Los días de semana deben estar entre 1 (Lunes) y 7 (Domingo)")
        return sorted(set(v))  # Remove duplicates and sort
    
    @field_validator("precio_min", "precio_max")
    @classmethod
    def validate_precios(cls, v: Optional[int], info) -> Optional[int]:
        """Validate prices."""
        if v is not None and v < 0:
            raise ValueError("El precio no puede ser negativo")
        
        # Check that min <= max
        if info.field_name == "precio_max" and v is not None:
            precio_min = info.data.get("precio_min")
            if precio_min is not None and v < precio_min:
                raise ValueError("El precio máximo no puede ser menor que el precio mínimo")
        
        return v
    
    @property
    def es_gratis(self) -> bool:
        """Check if event is free."""
        if self.precio:
            return "gratis" in self.precio.lower() or "free" in self.precio.lower()
        return self.precio_min == 0 or (self.precio_min == 0 and self.precio_max == 0)
    
    @property
    def esta_activo(self) -> bool:
        """Check if event is currently active (today between dates)."""
        if not self.activo:
            return False
        
        today = date.today()
        if self.fecha_inicio <= today <= (self.fecha_fin or self.fecha_inicio):
            return True
        return False
    
    def get_precio_range(self) -> str:
        """Get formatted price range string."""
        if self.es_gratis:
            return "Gratis"
        
        if self.precio_min and self.precio_max:
            if self.precio_min == self.precio_max:
                return f"${self.precio_min:,} COP".replace(",", ".")
            return f"${self.precio_min:,} - ${self.precio_max:,} COP".replace(",", ".")
        elif self.precio_min:
            return f"Desde ${self.precio_min:,} COP".replace(",", ".")
        elif self.precio_max:
            return f"Hasta ${self.precio_max:,} COP".replace(",", ".")
        return self.precio or "Consultar"
    
    def get_fecha_str(self) -> str:
        """Get formatted date string."""
        if self.fecha_fin and self.fecha_fin != self.fecha_inicio:
            return f"{self.fecha_inicio.strftime('%d/%m/%Y')} - {self.fecha_fin.strftime('%d/%m/%Y')}"
        return self.fecha_inicio.strftime('%d/%m/%Y')
    
    def get_horario_str(self) -> str:
        """Get formatted schedule string."""
        if self.hora_inicio and self.hora_fin:
            return f"{self.hora_inicio} - {self.hora_fin}"
        elif self.hora_inicio:
            return f"Desde {self.hora_inicio}"
        elif self.hora_fin:
            return f"Hasta {self.hora_fin}"
        return "Horario por confirmar"
    
    def get_dias_semana_str(self) -> str:
        """Get formatted days of week string."""
        if not self.dias_semana:
            return ""
        
        dias = [DiaSemana.get_display_name(d) for d in self.dias_semana]
        if len(dias) == 1:
            return dias[0]
        return ", ".join(dias)


class EventoCreate(EventoBase):
    """Model for creating a new Evento."""
    
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


class EventoUpdate(BaseModel):
    """Model for updating an existing Evento."""
    
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = None
    descripcion: Optional[str] = Field(None, min_length=10)
    descripcion_corta: Optional[str] = Field(None, max_length=300)
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    es_recurrente: Optional[bool] = None
    frecuencia: Optional[EventoFrecuencia] = None
    dias_semana: Optional[List[int]] = None
    ubicacion: Optional[str] = Field(None, max_length=300)
    direccion: Optional[str] = Field(None, max_length=500)
    lugar_id: Optional[int] = None
    latitud: Optional[float] = Field(None, ge=-90, le=90)
    longitud: Optional[float] = Field(None, ge=-180, le=180)
    precio: Optional[str] = Field(None, max_length=100)
    precio_min: Optional[int] = Field(None, ge=0)
    precio_max: Optional[int] = Field(None, ge=0)
    capacidad: Optional[int] = Field(None, ge=1)
    tags: Optional[List[str]] = None
    categoria_id: Optional[int] = None
    icono: Optional[str] = Field(None, max_length=10)
    imagen: Optional[str] = None
    imagenes: Optional[List[str]] = None
    video_url: Optional[str] = None
    organizador: Optional[str] = Field(None, max_length=200)
    contacto_email: Optional[str] = Field(None, max_length=200)
    contacto_telefono: Optional[str] = Field(None, max_length=50)
    sitio_web: Optional[str] = Field(None, max_length=300)
    instagram: Optional[str] = Field(None, max_length=100)
    destacado: Optional[bool] = None
    activo: Optional[bool] = None


# =====================================================
# DATABASE MODEL (for response/DB operations)
# =====================================================

class EventoInDB(EventoBase):
    """Model representing an Evento as stored in the database."""
    
    id: int = Field(..., description="ID único del evento")
    slug: str = Field(..., description="Slug URL-friendly")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    
    model_config = ConfigDict(from_attributes=True)


class EventoWithLugar(EventoInDB):
    """Extended model with place information."""
    
    lugar_nombre: Optional[str] = Field(None, description="Nombre del lugar asociado")
    lugar_direccion: Optional[str] = Field(None, description="Dirección del lugar asociado")
    categoria_nombre: Optional[str] = Field(None, description="Nombre de la categoría")


# =====================================================
# FILTERS MODEL
# =====================================================

class EventoFilters(BaseModel):
    """Filters for querying eventos."""
    
    busqueda: Optional[str] = Field(None, description="Búsqueda por texto en nombre/descripción")
    categoria: Optional[str] = Field(None, description="Filtrar por slug de categoría")
    tags: Optional[List[str]] = Field(None, description="Filtrar por tags")
    desde: Optional[date] = Field(None, description="Fecha de inicio mínima")
    hasta: Optional[date] = Field(None, description="Fecha de inicio máxima")
    destacados: Optional[bool] = Field(None, description="Solo eventos destacados")
    activos: bool = Field(default=True, description="Solo eventos activos")
    proximos: bool = Field(default=True, description="Solo eventos próximos")
    gratuitos: Optional[bool] = Field(None, description="Solo eventos gratuitos")
    limit: int = Field(default=20, ge=1, le=100, description="Límite de resultados")
    offset: int = Field(default=0, ge=0, description="Desplazamiento para paginación")
    
    @property
    def has_search(self) -> bool:
        """Check if search term is provided."""
        return self.busqueda is not None and len(self.busqueda.strip()) > 0
    
    @property
    def has_tags(self) -> bool:
        """Check if tags filters are provided."""
        return self.tags is not None and len(self.tags) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert filters to dictionary for Supabase query."""
        result = {}
        
        if self.categoria:
            result["categoria_slug"] = self.categoria
        
        if self.destacados is not None:
            result["destacado"] = self.destacados
        
        if self.activos is not None:
            result["activo"] = self.activos
        
        return result


# =====================================================
# RESPONSE MODELS
# =====================================================

class EventoListResponse(BaseModel):
    """Response model for list of eventos."""
    
    total: int = Field(..., description="Número total de resultados")
    limit: int = Field(..., description="Límite aplicado")
    offset: int = Field(..., description="Desplazamiento aplicado")
    results: List[EventoWithLugar] = Field(..., description="Lista de eventos")


class EventoProximosResponse(BaseModel):
    """Response model for upcoming events."""
    
    hoy: List[EventoWithLugar] = Field(default_factory=list, description="Eventos que ocurren hoy")
    manana: List[EventoWithLugar] = Field(default_factory=list, description="Eventos que ocurren mañana")
    esta_semana: List[EventoWithLugar] = Field(default_factory=list, description="Eventos esta semana")
    proximos_meses: List[EventoWithLugar] = Field(default_factory=list, description="Eventos próximos meses")


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_eventos_destacados_predefinidos() -> List[Dict[str, Any]]:
    """Get predefined highlighted events for Cali."""
    return [
        {
            "nombre": "Feria de Cali 2026",
            "fecha_inicio": date(2026, 12, 25),
            "fecha_fin": date(2026, 12, 30),
            "descripcion": "La feria más importante de Colombia. Salsódromo, cabalgata, conciertos y cultura caleña.",
            "ubicacion": "Toda la ciudad",
            "destacado": True,
            "icono": "🎉",
            "tags": ["Cultura", "Fiesta", "Salsa"]
        },
        {
            "nombre": "Festival Mundial de Salsa 2026",
            "fecha_inicio": date(2026, 9, 24),
            "fecha_fin": date(2026, 9, 28),
            "descripcion": "El evento de salsa más grande del mundo. Competencias, conciertos y clases magistrales.",
            "ubicacion": "Coliseo El Pueblo",
            "destacado": True,
            "icono": "🎺",
            "tags": ["Salsa", "Música", "Competencia"]
        },
        {
            "nombre": "Festival Petronio Álvarez",
            "fecha_inicio": date(2026, 8, 14),
            "fecha_fin": date(2026, 8, 19),
            "descripcion": "Celebración de la música del Pacífico. Currulao, marimba y gastronomía afrocolombiana.",
            "ubicacion": "Unidad Deportiva",
            "destacado": True,
            "icono": "🪘",
            "tags": ["Cultura", "Pacífico", "Música"]
        },
        {
            "nombre": "Salsa al Parque",
            "fecha_inicio": date(2026, 12, 10),
            "fecha_fin": date(2026, 12, 15),
            "descripcion": "Festival gratuito de salsa en espacios públicos. Orquestas en vivo y baile callejero.",
            "ubicacion": "Parque del Perro",
            "destacado": True,
            "icono": "🎷",
            "tags": ["Salsa", "Gratis", "Calle"]
        },
        {
            "nombre": "Tour Gastronómico del Pacífico",
            "fecha_inicio": date(2026, 1, 1),
            "fecha_fin": date(2026, 12, 31),
            "descripcion": "Ruta guiada por mercados y restaurantes. Encocado, arrechón, ceviche y lulada.",
            "ubicacion": "Mercado Alameda",
            "destacado": False,
            "es_recurrente": True,
            "frecuencia": "semanal",
            "dias_semana": [6],  # Sábados
            "icono": "🥘",
            "tags": ["Gastronomía", "Tour", "Pacífico"]
        }
    ]


# =====================================================
# CONSTANTS
# =====================================================

# Colores por tipo de evento
EVENTO_COLORS = {
    "salsa": "#9B59B6",
    "cultura": "#FF6B35",
    "musica": "#3498DB",
    "gastronomia": "#E74C3C",
    "deportes": "#2ECC71",
    "feria": "#F7931E",
    "gratis": "#27AE60"
}

# Tags populares para filtros
POPULAR_TAGS = [
    "Salsa", "Cultura", "Música", "Gastronomía", 
    "Gratis", "Familiar", "Nocturno", "Deportes",
    "Arte", "Tradición", "Pacífico", "Festival"
]


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("Evento model loaded successfully")
    print(f"Available frequencies: {EventoFrecuencia.list_values()}")
    
    # Test example creation
    test_evento = EventoCreate(
        nombre="Feria de Cali 2026",
        descripcion="La feria más salsera del mundo",
        fecha_inicio=date(2026, 12, 25),
        fecha_fin=date(2026, 12, 30),
        ubicacion="Toda la ciudad",
        precio="Eventos gratuitos"
    )
    print(f"\nTest evento created: {test_evento.nombre}")
    print(f"Generated slug: {test_evento.slug}")
    print(f"Date string: {test_evento.get_fecha_str()}")
    print(f"Is free: {test_evento.es_gratis}")
    
    # Test filters
    filters = EventoFilters(categoria="salsa", destacados=True)
    print(f"\nFilters: {filters.to_dict()}")
    
    # Test recurring event
    recurrente = EventoCreate(
        nombre="Clases de Salsa",
        descripcion="Clases de salsa todos los sábados",
        fecha_inicio=date(2026, 1, 1),
        es_recurrente=True,
        frecuencia="semanal",
        dias_semana=[6],
        ubicacion="La Topa Tolondra"
    )
    print(f"\nRecurring event: {recurrente.nombre}")
    print(f"Days: {recurrente.get_dias_semana_str()}")
    
    # Test predefined events
    print("\nPredefined events:")
    for evento in get_eventos_destacados_predefinidos():
        print(f"  {evento['icono']} {evento['nombre']}")