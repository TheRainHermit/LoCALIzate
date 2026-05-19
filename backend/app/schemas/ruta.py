"""
Ruta Schemas for LoCALIzate Backend
==================================

Pydantic models for routes and itineraries request/response validation.

Schemas:
    - RutaBase: Base fields for ruta
    - RutaCreate: Creation request
    - RutaUpdate: Update request
    - RutaResponse: Basic response
    - RutaDetailResponse: Detailed response with steps
    - RutaListResponse: Paginated list response
    - RutaOptimizarRequest: Route optimization request
    - RutaOptimizadaResponse: Optimized route response
    - RutaStepResponse: Individual step in route
    - RutaGuardadaResponse: Saved route response
    - RutaTemplateResponse: Predefined route template
    - ModoTransporte: Transport mode enum
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


# =====================================================
# ENUMS
# =====================================================

class ModoTransporte(str, Enum):
    """Transportation modes for route calculation."""
    CAMINANDO = "walking"
    BICICLETA = "biking"
    AUTO = "driving"
    TRANSPORTE_PUBLICO = "public"
    
    @classmethod
    def list_values(cls) -> List[str]:
        return [item.value for item in cls]
    
    @classmethod
    def get_display_name(cls, value: str) -> str:
        """Get display name in Spanish."""
        names = {
            "walking": "Caminando",
            "biking": "Bicicleta",
            "driving": "Auto",
            "public": "Transporte público"
        }
        return names.get(value, value)
    
    @property
    def velocidad_kmh(self) -> float:
        """Average speed in km/h."""
        speeds = {
            ModoTransporte.CAMINANDO: 5.0,
            ModoTransporte.BICICLETA: 15.0,
            ModoTransporte.AUTO: 30.0,
            ModoTransporte.TRANSPORTE_PUBLICO: 20.0
        }
        return speeds.get(self, 5.0)


# =====================================================
# BASE SCHEMAS
# =====================================================

class RutaBase(BaseModel):
    """Base schema with common fields for ruta."""
    
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
    """Schema for creating a new ruta."""
    
    lugar_ids: List[int] = Field(..., min_length=1, max_length=20, description="IDs de lugares en orden de preferencia")
    
    @field_validator("lugar_ids")
    @classmethod
    def validate_lugar_ids(cls, v: List[int]) -> List[int]:
        """Validate place IDs list."""
        if len(v) != len(set(v)):
            raise ValueError("No se permiten lugares duplicados en la ruta")
        return v


class RutaUpdate(BaseModel):
    """Schema for updating an existing ruta."""
    
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=500)
    fecha_visita: Optional[date] = None
    hora_inicio: Optional[str] = None
    completada: Optional[bool] = None
    compartida: Optional[bool] = None
    activa: Optional[bool] = None


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class RutaStepResponse(BaseModel):
    """Individual step in a route."""
    
    orden: int = Field(..., description="Orden de visita")
    lugar_id: int = Field(..., description="ID del lugar")
    nombre: str = Field(..., description="Nombre del lugar")
    lat: float = Field(..., description="Latitud")
    lng: float = Field(..., description="Longitud")
    distancia_km: float = Field(..., description="Distancia desde punto anterior en km")
    distancia_formateada: str = Field(..., description="Distancia formateada (ej: '2.5 km')")
    tiempo_min: int = Field(..., description="Tiempo estimado desde punto anterior en minutos")
    tiempo_formateado: str = Field(..., description="Tiempo formateado (ej: '1h 30min')")
    instruccion: str = Field(..., description="Instrucción de navegación")


class RutaResponse(BaseModel):
    """Basic response schema for ruta."""
    
    id: int
    nombre: str
    descripcion: Optional[str]
    fecha_visita: Optional[str]
    hora_inicio: Optional[str]
    distancia_total_km: float
    tiempo_total_min: int
    tiempo_formateado: str
    cantidad_lugares: int
    completada: bool
    compartida: bool
    created_at: str
    
    model_config = ConfigDict(from_attributes=True)


class RutaDetailResponse(RutaResponse):
    """Detailed response schema for ruta with steps."""
    
    pasos: List[RutaStepResponse] = Field(default_factory=list, description="Pasos de la ruta")


class RutaListResponse(BaseModel):
    """Paginated list response for rutas."""
    
    total: int
    limit: int
    offset: int
    results: List[RutaResponse]


# =====================================================
# OPTIMIZATION SCHEMAS
# =====================================================

class RutaOptimizarRequest(BaseModel):
    """Request schema for route optimization."""
    
    lugares_ids: List[int] = Field(..., min_length=1, max_length=15, description="IDs de lugares a visitar")
    origen_lat: float = Field(..., ge=-90, le=90, description="Latitud de origen")
    origen_lng: float = Field(..., ge=-180, le=180, description="Longitud de origen")
    modo: ModoTransporte = Field(default=ModoTransporte.CAMINANDO, description="Modo de transporte")
    retornar_origen: bool = Field(default=False, description="Si debe retornar al punto de inicio")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lugares_ids": [1, 2, 3],
                "origen_lat": 3.4516,
                "origen_lng": -76.5320,
                "modo": "walking",
                "retornar_origen": False
            }
        }
    )


class RutaOptimizadaResponse(BaseModel):
    """Response schema for optimized route."""
    
    lugares_ordenados: List[RutaStepResponse] = Field(..., description="Lugares en orden optimizado")
    distancia_total_km: float = Field(..., description="Distancia total en km")
    tiempo_total_min: int = Field(..., description="Tiempo total en minutos")
    tiempo_formateado: str = Field(..., description="Tiempo formateado")
    cantidad_lugares: int = Field(..., description="Número de lugares")
    modo_transporte: str = Field(..., description="Modo de transporte")
    modo_nombre: str = Field(..., description="Nombre del modo en español")
    advertencias: List[str] = Field(default_factory=list, description="Advertencias")


class RutaGuardadaResponse(BaseModel):
    """Response schema for saved route."""
    
    id: int
    nombre: str
    descripcion: Optional[str]
    fecha_visita: Optional[str]
    hora_inicio: Optional[str]
    distancia_total_km: float
    tiempo_total_min: int
    tiempo_formateado: str
    cantidad_lugares: int
    completada: bool
    compartida: bool
    created_at: str


# =====================================================
# TEMPLATE SCHEMAS
# =====================================================

class RutaTemplateResponse(BaseModel):
    """Response schema for predefined route template."""
    
    id: int
    nombre: str
    descripcion: str
    duracion_horas: int
    dificultad: str  # 'fácil', 'media', 'difícil'
    categoria: str
    icono: str
    lugares_sugeridos: List[int]
    imagen: Optional[str] = None


class DistanciaResponse(BaseModel):
    """Response schema for distance calculation between two points."""
    
    distancia_km: float
    distancia_formateada: str
    tiempo_caminando_min: int
    tiempo_caminando_formateado: str
    tiempo_bicicleta_min: int
    tiempo_auto_min: int
    desde: Dict[str, float]
    hasta: Dict[str, float]


# =====================================================
# ROUTE DETAIL SCHEMAS
# =====================================================

class RutaDetalleBase(BaseModel):
    """Base schema for route detail (place in route)."""
    
    orden: int = Field(..., ge=1, description="Orden de visita")
    lugar_id: int = Field(..., description="ID del lugar")
    distancia_desde_anterior_km: Optional[float] = Field(None, ge=0)
    tiempo_estimado_min: Optional[int] = Field(None, ge=0)
    notas: Optional[str] = Field(None, max_length=500)
    visitado: bool = Field(default=False)


class RutaDetalleCreate(RutaDetalleBase):
    """Schema for creating route detail."""
    pass


class RutaDetalleResponse(RutaDetalleBase):
    """Response schema for route detail."""
    
    id: int
    ruta_id: int
    lugar_nombre: Optional[str] = None
    lugar_latitud: Optional[float] = None
    lugar_longitud: Optional[float] = None
    lugar_icono: Optional[str] = None
    lugar_direccion: Optional[str] = None
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def formatear_distancia(distancia_km: float) -> str:
    """Format distance for display."""
    if distancia_km < 0.1:
        return f"{int(distancia_km * 1000)} m"
    return f"{distancia_km:.1f} km"


def formatear_tiempo(tiempo_min: int) -> str:
    """Format time for display."""
    if tiempo_min < 60:
        return f"{tiempo_min} min"
    horas = tiempo_min // 60
    minutos = tiempo_min % 60
    if minutos == 0:
        return f"{horas}h"
    return f"{horas}h {minutos}min"


# Predefined route templates
PREDEFINED_ROUTE_TEMPLATES = [
    {
        "id": 1,
        "nombre": "Tour Cultural por el Centro",
        "descripcion": "Recorrido por los principales sitios culturales e históricos del centro de Cali",
        "duracion_horas": 4,
        "dificultad": "fácil",
        "categoria": "cultura",
        "icono": "🎭",
        "lugares_sugeridos": [3, 2, 7, 1]
    },
    {
        "id": 2,
        "nombre": "Naturaleza y Aventura",
        "descripcion": "Descubre los espacios naturales más impresionantes de Cali",
        "duracion_horas": 6,
        "dificultad": "media",
        "categoria": "naturaleza",
        "icono": "🌳",
        "lugares_sugeridos": [4, 6]
    },
    {
        "id": 3,
        "nombre": "Ruta Salsera",
        "descripcion": "Vive la experiencia de la salsa caleña en sus mejores lugares",
        "duracion_horas": 5,
        "dificultad": "fácil",
        "categoria": "salsa",
        "icono": "💃",
        "lugares_sugeridos": [12, 13, 14]
    },
    {
        "id": 4,
        "nombre": "Gastronomía Caleña",
        "descripcion": "Los mejores sabores de la cocina del Pacífico y caleña",
        "duracion_horas": 4,
        "dificultad": "fácil",
        "categoria": "gastronomia",
        "icono": "🍽️",
        "lugares_sugeridos": [11, 15, 16]
    },
    {
        "id": 5,
        "nombre": "Aventura Extrema",
        "descripcion": "Para los amantes de la adrenalina y las experiencias únicas",
        "duracion_horas": 8,
        "dificultad": "difícil",
        "categoria": "aventura",
        "icono": "🧗",
        "lugares_sugeridos": [17, 18, 10]
    }
]


def get_route_templates() -> List[Dict[str, Any]]:
    """Get all predefined route templates."""
    return PREDEFINED_ROUTE_TEMPLATES.copy()


def get_route_template_by_category(categoria: str) -> List[Dict[str, Any]]:
    """Get route templates by category."""
    return [t for t in PREDEFINED_ROUTE_TEMPLATES if t["categoria"] == categoria]


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("Ruta schemas loaded successfully")
    print(f"Available transport modes: {ModoTransporte.list_values()}")
    
    # Test route creation
    test_ruta = RutaCreate(
        nombre="Mi Ruta de Prueba",
        descripcion="Probando el modelo de ruta",
        lugar_ids=[1, 2, 3]
    )
    print(f"\nTest route created: {test_ruta.nombre}")
    print(f"Places: {test_ruta.lugar_ids}")
    
    # Test optimization request
    test_request = RutaOptimizarRequest(
        lugares_ids=[1, 2, 3],
        origen_lat=3.4516,
        origen_lng=-76.5320,
        modo=ModoTransporte.CAMINANDO
    )
    print(f"\nOptimization request: {test_request.lugares_ids}")
    print(f"Mode: {test_request.modo.value}")
    
    # Test step response
    test_step = RutaStepResponse(
        orden=1,
        lugar_id=1,
        nombre="Cristo Rey",
        lat=3.43587,
        lng=-76.56490,
        distancia_km=2.5,
        distancia_formateada="2.5 km",
        tiempo_min=30,
        tiempo_formateado="30 min",
        instruccion="Dirígete hacia el sur"
    )
    print(f"\nRoute step: {test_step.nombre}")
    
    # Test templates
    print("\nPredefined route templates:")
    for template in get_route_templates():
        print(f"  {template['icono']} {template['nombre']} ({template['duracion_horas']}h)")
    
    print("\n✅ Ruta schemas ready")