"""
Ruta Model for LoCALIzate Backend
================================

Model representing user-created itineraries and optimized routes
for visiting tourist places in Cali.

Features:
    - User can create custom routes with selected places
    - Automatic optimization of visit order (nearest neighbor algorithm)
    - Distance and time calculations between places
    - Route sharing and saving for future reference

Fields:
    - Basic: id, nombre, descripcion, usuario_id
    - Schedule: fecha_visita, hora_inicio
    - Metrics: distancia_total_km, tiempo_estimado_min
    - Status: completada, compartida, activa
    - Details: list of places in order with visit metadata
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from math import radians, sin, cos, sqrt, atan2
from pydantic import BaseModel, Field, field_validator, ConfigDict


# =====================================================
# HELPER FUNCTIONS
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


def calcular_tiempo_estimado(distancia_km: float, velocidad_kmh: float = 30.0) -> int:
    """
    Calculate estimated time in minutes based on distance.
    
    Args:
        distancia_km: Distance in kilometers
        velocidad_kmh: Average speed in km/h (default 30 km/h for city driving)
    
    Returns:
        Estimated time in minutes
    """
    return int((distancia_km / velocidad_kmh) * 60)


# =====================================================
# BASE MODELS
# =====================================================

class RutaBase(BaseModel):
    """Base model for Ruta with common fields."""
    
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre de la ruta")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción de la ruta")
    
    # Schedule
    fecha_visita: Optional[date] = Field(None, description="Fecha planificada para la visita")
    hora_inicio: Optional[str] = Field(None, description="Hora de inicio planificada (HH:MM)")
    
    # Status
    completada: bool = Field(default=False, description="Si la ruta fue completada")
    compartida: bool = Field(default=False, description="Si la ruta es pública/compartida")
    activa: bool = Field(default=True, description="Si la ruta está activa")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Tour Cultural por Cali",
                "descripcion": "Recorrido por los principales sitios culturales de la ciudad",
                "fecha_visita": "2026-06-15",
                "hora_inicio": "09:00"
            }
        }
    )
    
    @field_validator("hora_inicio")
    @classmethod
    def validate_hora_inicio(cls, v: Optional[str]) -> Optional[str]:
        """Validate time format HH:MM."""
        if v is None:
            return v
        
        import re
        if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError("Formato de hora inválido. Use HH:MM (ejemplo: 09:00)")
        return v


class RutaCreate(RutaBase):
    """Model for creating a new Ruta."""
    
    lugar_ids: List[int] = Field(..., min_length=1, max_length=20, description="IDs de lugares en orden de preferencia")
    
    @field_validator("lugar_ids")
    @classmethod
    def validate_lugar_ids(cls, v: List[int]) -> List[int]:
        """Validate place IDs list."""
        if len(v) != len(set(v)):
            raise ValueError("No se permiten lugares duplicados en la ruta")
        return v


class RutaUpdate(BaseModel):
    """Model for updating an existing Ruta."""
    
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=500)
    fecha_visita: Optional[date] = None
    hora_inicio: Optional[str] = None
    completada: Optional[bool] = None
    compartida: Optional[bool] = None
    activa: Optional[bool] = None


# =====================================================
# RUTA DETALLE MODELS
# =====================================================

class RutaDetalleBase(BaseModel):
    """Base model for RutaDetalle (places in a route)."""
    
    orden: int = Field(..., ge=1, description="Orden de visita en la ruta")
    lugar_id: int = Field(..., description="ID del lugar")
    lugar_nombre: Optional[str] = Field(None, description="Nombre del lugar (para respuestas)")
    lugar_latitud: Optional[float] = Field(None, description="Latitud del lugar")
    lugar_longitud: Optional[float] = Field(None, description="Longitud del lugar")
    lugar_icono: Optional[str] = Field(None, description="Icono del lugar")
    lugar_direccion: Optional[str] = Field(None, description="Dirección del lugar")
    
    # Calculated fields
    distancia_desde_anterior_km: Optional[float] = Field(None, ge=0, description="Distancia desde el punto anterior")
    tiempo_estimado_min: Optional[int] = Field(None, ge=0, description="Tiempo estimado desde punto anterior")
    
    # User notes
    notas: Optional[str] = Field(None, max_length=500, description="Notas personales del usuario")
    visitado: bool = Field(default=False, description="Si el lugar ya fue visitado")
    hora_llegada_estimada: Optional[str] = Field(None, description="Hora estimada de llegada")
    
    model_config = ConfigDict(from_attributes=True)


class RutaDetalleCreate(RutaDetalleBase):
    """Model for creating RutaDetalle."""
    pass


class RutaDetalleInDB(RutaDetalleBase):
    """Model for RutaDetalle as stored in database."""
    
    id: int
    ruta_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =====================================================
# DATABASE MODELS (for response/DB operations)
# =====================================================

class RutaInDB(RutaBase):
    """Model representing a Ruta as stored in the database."""
    
    id: int = Field(..., description="ID único de la ruta")
    usuario_id: str = Field(..., description="ID del usuario que creó la ruta")
    
    # Metrics
    distancia_total_km: float = Field(default=0.0, ge=0, description="Distancia total en kilómetros")
    tiempo_estimado_min: int = Field(default=0, ge=0, description="Tiempo total estimado en minutos")
    
    # Timestamps
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    
    model_config = ConfigDict(from_attributes=True)


class RutaWithDetalles(RutaInDB):
    """Extended route model with details (places in order)."""
    
    detalles: List[RutaDetalleInDB] = Field(default_factory=list, description="Lugares en la ruta con orden")
    
    @property
    def cantidad_lugares(self) -> int:
        """Get number of places in the route."""
        return len(self.detalles)
    
    @property
    def tiempo_formateado(self) -> str:
        """Get formatted time string (e.g., '2h 30min')."""
        horas = self.tiempo_estimado_min // 60
        minutos = self.tiempo_estimado_min % 60
        
        if horas > 0:
            return f"{horas}h {minutos}min"
        return f"{minutos}min"
    
    def get_itinerario(self) -> List[Dict[str, Any]]:
        """Get itinerary with detailed information for each stop."""
        itinerary = []
        prev_time = None
        
        for detalle in sorted(self.detalles, key=lambda x: x.orden):
            stop = {
                "orden": detalle.orden,
                "lugar_id": detalle.lugar_id,
                "lugar_nombre": detalle.lugar_nombre,
                "lugar_icono": detalle.lugar_icono,
                "distancia_desde_anterior": detalle.distancia_desde_anterior_km,
                "tiempo_desde_anterior": detalle.tiempo_estimado_min,
                "notas": detalle.notas,
                "visitado": detalle.visitado
            }
            
            # Calculate arrival time if route has start time
            if detalle.hora_llegada_estimada:
                stop["hora_llegada"] = detalle.hora_llegada_estimada
            elif self.hora_inicio and detalle.orden == 1:
                stop["hora_llegada"] = self.hora_inicio
            elif prev_time and detalle.tiempo_estimado_min:
                # Calculate next arrival time (simplified)
                stop["hora_llegada"] = "Calculado en backend"
            
            itinerary.append(stop)
            prev_time = stop.get("hora_llegada")
        
        return itinerary


# =====================================================
# OPTIMIZED ROUTE MODELS
# =====================================================

class LugarParaRuta(BaseModel):
    """Place information for route optimization."""
    
    id: int
    nombre: str
    latitud: float
    longitud: float
    icono: str = "📍"
    horario: Optional[str] = None
    tiempo_estimado_visita_min: int = Field(default=60, description="Tiempo estimado de visita en minutos")
    
    model_config = ConfigDict(from_attributes=True)


class RutaStep(BaseModel):
    """Single step in an optimized route."""
    
    orden: int
    lugar_id: int
    lugar_nombre: str
    lugar_icono: str
    latitud: float
    longitud: float
    distancia_desde_anterior_km: float
    tiempo_desplazamiento_min: int
    tiempo_visita_min: int
    hora_llegada_estimada: Optional[str] = None
    horario_lugar: Optional[str] = None
    
    @property
    def tiempo_total_min(self) -> int:
        """Total time for this step (travel + visit)."""
        return self.tiempo_desplazamiento_min + self.tiempo_visita_min


class RutaOptimizada(BaseModel):
    """Complete optimized route response."""
    
    nombre: str
    descripcion: Optional[str] = None
    inicio_lat: float
    inicio_lng: float
    inicio_direccion: Optional[str] = None
    
    steps: List[RutaStep]
    
    distancia_total_km: float
    tiempo_desplazamiento_total_min: int
    tiempo_visita_total_min: int
    
    @property
    def tiempo_total_min(self) -> int:
        """Total time including travel and visits."""
        return self.tiempo_desplazamiento_total_min + self.tiempo_visita_total_min
    
    @property
    def cantidad_lugares(self) -> int:
        """Number of places in the route."""
        return len(self.steps)
    
    @property
    def tiempo_formateado(self) -> str:
        """Get formatted total time string."""
        horas = self.tiempo_total_min // 60
        minutos = self.tiempo_total_min % 60
        
        if horas > 0:
            return f"{horas}h {minutos}min"
        return f"{minutos}min"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "inicio": {
                "lat": self.inicio_lat,
                "lng": self.inicio_lng,
                "direccion": self.inicio_direccion
            },
            "steps": [step.model_dump() for step in self.steps],
            "resumen": {
                "distancia_total_km": round(self.distancia_total_km, 2),
                "tiempo_desplazamiento_min": self.tiempo_desplazamiento_total_min,
                "tiempo_visita_min": self.tiempo_visita_total_min,
                "tiempo_total_min": self.tiempo_total_min,
                "tiempo_formateado": self.tiempo_formateado,
                "cantidad_lugares": self.cantidad_lugares
            }
        }


# =====================================================
# ROUTE OPTIMIZATION REQUEST/RESPONSE
# =====================================================

class OptimizarRutaRequest(BaseModel):
    """Request model for route optimization."""
    
    lugar_ids: List[int] = Field(..., min_length=1, max_length=15, description="IDs de lugares a visitar")
    inicio_lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitud de inicio")
    inicio_lng: Optional[float] = Field(None, ge=-180, le=180, description="Longitud de inicio")
    inicio_direccion: Optional[str] = Field(None, description="Dirección de inicio")
    hora_salida: Optional[str] = Field(None, description="Hora de salida (HH:MM)")
    tiempo_por_lugar_min: int = Field(default=60, ge=15, le=240, description="Tiempo estimado por lugar en minutos")
    optimizar: bool = Field(default=True, description="Si se debe optimizar el orden")
    
    @property
    def tiene_inicio_personalizado(self) -> bool:
        """Check if custom start location is provided."""
        return self.inicio_lat is not None and self.inicio_lng is not None


class OptimizarRutaResponse(BaseModel):
    """Response model for route optimization."""
    
    ruta_optimizada: RutaOptimizada
    advertencias: List[str] = Field(default_factory=list)
    sugerencias: List[str] = Field(default_factory=list)


# =====================================================
# RESPONSE MODELS
# =====================================================

class RutaListResponse(BaseModel):
    """Response model for list of routes."""
    
    total: int
    limit: int
    offset: int
    results: List[RutaWithDetalles]


class RutaSimpleResponse(BaseModel):
    """Simple route response for lists."""
    
    id: int
    nombre: str
    descripcion: Optional[str]
    fecha_visita: Optional[date]
    cantidad_lugares: int
    distancia_total_km: float
    tiempo_formateado: str
    completada: bool
    compartida: bool
    created_at: datetime
    
    @classmethod
    def from_ruta(cls, ruta: RutaWithDetalles) -> "RutaSimpleResponse":
        """Create from RutaWithDetalles."""
        return cls(
            id=ruta.id,
            nombre=ruta.nombre,
            descripcion=ruta.descripcion,
            fecha_visita=ruta.fecha_visita,
            cantidad_lugares=ruta.cantidad_lugares,
            distancia_total_km=ruta.distancia_total_km,
            tiempo_formateado=ruta.tiempo_formateado,
            completada=ruta.completada,
            compartida=ruta.compartida,
            created_at=ruta.created_at
        )


# =====================================================
# ROUTE TEMPLATES (Predefined routes)
# =====================================================

class RutaTemplate(BaseModel):
    """Predefined route template for recommendations."""
    
    id: int
    nombre: str
    descripcion: str
    duracion_horas: int
    dificultad: str  # 'fácil', 'media', 'difícil'
    categoria: str
    icono: str
    lugares_sugeridos: List[int]
    imagen: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# Predefined route templates for Cali
PREDEFINED_ROUTE_TEMPLATES = [
    {
        "id": 1,
        "nombre": "Tour Cultural por el Centro",
        "descripcion": "Recorrido por los principales sitios culturales e históricos del centro de Cali",
        "duracion_horas": 4,
        "dificultad": "fácil",
        "categoria": "cultura",
        "icono": "🎭",
        "lugares_sugeridos": [3, 2, 7, 1]  # Iglesia La Ermita, Gato del Río, San Antonio, Cristo Rey
    },
    {
        "id": 2,
        "nombre": "Naturaleza y Aventura",
        "descripcion": "Descubre los espacios naturales más impresionantes de Cali",
        "duracion_horas": 6,
        "dificultad": "media",
        "categoria": "naturaleza",
        "icono": "🌳",
        "lugares_sugeridos": [4, 6]  # Río Pance, Zoológico
    },
    {
        "id": 3,
        "nombre": "Ruta Salsera",
        "descripcion": "Vive la experiencia de la salsa caleña en sus mejores lugares",
        "duracion_horas": 5,
        "dificultad": "fácil",
        "categoria": "salsa",
        "icono": "💃",
        "lugares_sugeridos": [12, 13, 14]  # Plazoleta Jairo Varela, La Topa Tolondra, Tin Tin Deo
    },
    {
        "id": 4,
        "nombre": "Gastronomía Caleña",
        "descripcion": "Los mejores sabores de la cocina del Pacífico y caleña",
        "duracion_horas": 4,
        "dificultad": "fácil",
        "categoria": "gastronomia",
        "icono": "🍽️",
        "lugares_sugeridos": [11, 15, 16]  # Bulevar del Río, Morada Ancestral, Palomulata
    },
    {
        "id": 5,
        "nombre": "Aventura Extrema",
        "descripcion": "Para los amantes de la adrenalina y las experiencias únicas",
        "duracion_horas": 8,
        "dificultad": "difícil",
        "categoria": "aventura",
        "icono": "🧗",
        "lugares_sugeridos": [17, 18, 10]  # Parapente, Chorrera del Indio, Farallones
    }
]


def get_route_templates() -> List[RutaTemplate]:
    """Get all predefined route templates."""
    return [RutaTemplate(**template) for template in PREDEFINED_ROUTE_TEMPLATES]


def get_route_template_by_category(categoria: str) -> List[RutaTemplate]:
    """Get route templates by category."""
    return [t for t in get_route_templates() if t.categoria == categoria]


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("Ruta model loaded successfully")
    
    # Test distance calculation
    dist = haversine_distance(3.43587, -76.56490, 3.45156, -76.54297)
    print(f"Distance between Cristo Rey and Gato del Río: {dist:.2f} km")
    
    # Test route creation
    test_ruta = RutaCreate(
        nombre="Mi Ruta de Prueba",
        descripcion="Probando el modelo de ruta",
        lugar_ids=[1, 2, 3]
    )
    print(f"\nTest route created: {test_ruta.nombre}")
    print(f"Places: {test_ruta.lugar_ids}")
    
    # Test time calculation
    tiempo = calcular_tiempo_estimado(dist)
    print(f"\nEstimated travel time: {tiempo} minutes")
    
    # Test route step
    step = RutaStep(
        orden=1,
        lugar_id=1,
        lugar_nombre="Cristo Rey",
        lugar_icono="✝️",
        latitud=3.43587,
        longitud=-76.56490,
        distancia_desde_anterior_km=0,
        tiempo_desplazamiento_min=0,
        tiempo_visita_min=60,
        horario_lugar="8:00 AM - 6:00 PM"
    )
    print(f"\nRoute step: {step.lugar_nombre}")
    print(f"Total time: {step.tiempo_total_min} minutes")
    
    # Test templates
    print("\nPredefined route templates:")
    for template in get_route_templates():
        print(f"  {template.icono} {template.nombre} ({template.duracion_horas}h) - {template.dificultad}")
    
    print("\n✅ Ruta model ready")