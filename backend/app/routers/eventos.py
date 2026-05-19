"""
Endpoints para Eventos - LoCALIzate Backend
==========================================

Proporciona endpoints para gestionar eventos y festivales en Cali:
    - Listado de eventos con filtros (destacados, fechas, categorías)
    - Eventos próximos (hoy, esta semana, este mes)
    - Detalle de evento específico
    - Eventos destacados
    - Eventos por ubicación o lugar asociado

Dependencias:
    - EventoRepository: Acceso a datos de eventos
    - LugarRepository: Para obtener lugares asociados
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date, timedelta
import logging

from app.repositories.evento_repo import EventoRepository
from app.repositories.lugar_repo import LugarRepository
from app.core.database import get_db
from app.core.dependencies import get_current_user_optional, get_pagination, PaginationParams
from app.core.exceptions import NotFoundException, ValidationException

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/eventos", tags=["Eventos"])


# =====================================================
# PYDANTIC MODELS
# =====================================================

class EventoResponse(BaseModel):
    """Respuesta para un evento"""
    id: int
    nombre: str
    descripcion: str
    descripcion_corta: Optional[str] = None
    fecha_inicio: str
    fecha_fin: Optional[str] = None
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    ubicacion: Optional[str] = None
    direccion: Optional[str] = None
    lugar_id: Optional[int] = None
    lugar_nombre: Optional[str] = None
    precio: Optional[str] = None
    precio_min: Optional[int] = None
    precio_max: Optional[int] = None
    icono: str = "🎉"
    imagen: Optional[str] = None
    tags: Optional[List[str]] = None
    destacado: bool = False
    es_recurrente: bool = False
    frecuencia: Optional[str] = None
    
    class Config:
        from_attributes = True


class EventoDetalleResponse(EventoResponse):
    """Respuesta detallada para un evento"""
    organizador: Optional[str] = None
    contacto_email: Optional[str] = None
    contacto_telefono: Optional[str] = None
    sitio_web: Optional[str] = None
    instagram: Optional[str] = None
    capacidad: Optional[int] = None
    imagenes: Optional[List[str]] = None
    video_url: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    
    # Campos calculados
    esta_activo: bool = False
    es_gratis: bool = False
    fecha_formateada: str = ""
    horario_formateado: str = ""


class EventoListResponse(BaseModel):
    """Respuesta para listado de eventos"""
    total: int
    limit: int
    offset: int
    results: List[EventoResponse]


class EventoProximosResponse(BaseModel):
    """Respuesta para eventos próximos agrupados"""
    hoy: List[EventoResponse] = []
    manana: List[EventoResponse] = []
    esta_semana: List[EventoResponse] = []
    este_mes: List[EventoResponse] = []
    proximos_meses: List[EventoResponse] = []


class EventoCreateRequest(BaseModel):
    """Request para crear un evento (admin)"""
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: str = Field(..., min_length=10)
    descripcion_corta: Optional[str] = Field(None, max_length=300)
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    ubicacion: Optional[str] = None
    direccion: Optional[str] = None
    lugar_id: Optional[int] = None
    precio: Optional[str] = None
    precio_min: Optional[int] = Field(None, ge=0)
    precio_max: Optional[int] = Field(None, ge=0)
    icono: str = "🎉"
    imagen: Optional[str] = None
    tags: Optional[List[str]] = None
    destacado: bool = False
    es_recurrente: bool = False
    frecuencia: Optional[str] = None
    dias_semana: Optional[List[int]] = None


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _formatear_fecha(fecha: date) -> str:
    """Formatear fecha para mostrar."""
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    return f"{fecha.day} de {meses[fecha.month]} de {fecha.year}"


def _convertir_evento_response(evento: Dict[str, Any], incluir_lugar: bool = False) -> dict:
    """Convertir evento de BD a diccionario de respuesta."""
    resultado = {
        "id": evento.get('id'),
        "nombre": evento.get('nombre'),
        "descripcion": evento.get('descripcion'),
        "descripcion_corta": evento.get('descripcion_corta'),
        "fecha_inicio": evento.get('fecha_inicio'),
        "fecha_fin": evento.get('fecha_fin'),
        "hora_inicio": evento.get('hora_inicio'),
        "hora_fin": evento.get('hora_fin'),
        "ubicacion": evento.get('ubicacion'),
        "direccion": evento.get('direccion'),
        "lugar_id": evento.get('lugar_id'),
        "precio": evento.get('precio'),
        "precio_min": evento.get('precio_min'),
        "precio_max": evento.get('precio_max'),
        "icono": evento.get('icono', '🎉'),
        "imagen": evento.get('imagen'),
        "tags": evento.get('tags', []),
        "destacado": evento.get('destacado', False),
        "es_recurrente": evento.get('es_recurrente', False),
        "frecuencia": evento.get('frecuencia')
    }
    
    if incluir_lugar:
        resultado["lugar_nombre"] = evento.get('lugar_nombre')
        resultado["categoria_nombre"] = evento.get('categoria_nombre')
    
    return resultado


# =====================================================
# ENDPOINTS PÚBLICOS
# =====================================================

@router.get("/", response_model=EventoListResponse)
async def listar_eventos(
    destacados: Optional[bool] = Query(None, description="Solo eventos destacados"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    busqueda: Optional[str] = Query(None, description="Búsqueda por nombre o descripción"),
    desde: Optional[date] = Query(None, description="Fecha de inicio mínima"),
    hasta: Optional[date] = Query(None, description="Fecha de inicio máxima"),
    pagination: PaginationParams = Depends(get_pagination),
    supabase = Depends(get_db)
):
    """
    Listar eventos con filtros opcionales.
    
    - Destacados: Solo eventos destacados
    - Categoría: Filtrar por categoría
    - Búsqueda: Por nombre o descripción
    - Desde/Hasta: Rango de fechas
    """
    try:
        evento_repo = EventoRepository(supabase)
        
        # Construir filtros
        filters = {}
        if destacados is not None:
            filters["destacado"] = destacados
        if categoria:
            filters["categoria_slug"] = categoria
        
        # Obtener eventos
        query = evento_repo._table.select("*").eq("activo", True)
        
        for key, value in filters.items():
            if value is not None:
                query = query.eq(key, value)
        
        if desde:
            query = query.gte("fecha_inicio", desde.isoformat())
        if hasta:
            query = query.lte("fecha_inicio", hasta.isoformat())
        
        if busqueda:
            query = query.or_(f"nombre.ilike.%{busqueda}%,descripcion.ilike.%{busqueda}%")
        
        # Ordenar y paginar
        query = query.order("fecha_inicio")
        query = query.range(pagination.offset, pagination.offset + pagination.limit - 1)
        
        result = query.execute()
        eventos = result.data if result.data else []
        
        # Obtener total
        total = await evento_repo.get_count(filters={"activo": True})
        
        return EventoListResponse(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            results=[EventoResponse(**_convertir_evento_response(e)) for e in eventos]
        )
        
    except Exception as e:
        logger.error(f"Error en listar_eventos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/destacados", response_model=List[EventoResponse])
async def get_eventos_destacados(
    limit: int = Query(6, ge=1, le=20, description="Número de eventos destacados"),
    supabase = Depends(get_db)
):
    """
    Obtener eventos destacados (featured).
    """
    try:
        evento_repo = EventoRepository(supabase)
        
        eventos = await evento_repo.get_destacados(limit=limit)
        
        return [EventoResponse(**_convertir_evento_response(e)) for e in eventos]
        
    except Exception as e:
        logger.error(f"Error en get_eventos_destacados: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proximos", response_model=EventoProximosResponse)
async def get_eventos_proximos(
    dias: int = Query(30, ge=1, le=90, description="Días hacia adelante"),
    supabase = Depends(get_db)
):
    """
    Obtener eventos próximos agrupados por:
    - Hoy
    - Mañana
    - Esta semana
    - Este mes
    - Próximos meses
    """
    try:
        evento_repo = EventoRepository(supabase)
        
        hoy = date.today()
        manana = hoy + timedelta(days=1)
        fin_semana = hoy + timedelta(days=7 - hoy.weekday())
        fin_mes = date(hoy.year, hoy.month + 1, 1) - timedelta(days=1) if hoy.month < 12 else date(hoy.year, 12, 31)
        fecha_limite = hoy + timedelta(days=dias)
        
        # Obtener eventos en el rango
        eventos = await evento_repo.get_by_date_range(hoy, fecha_limite, limit=200)
        
        # Clasificar eventos
        hoy_list = []
        manana_list = []
        semana_list = []
        mes_list = []
        proximos_list = []
        
        for evento in eventos:
            fecha = datetime.fromisoformat(evento['fecha_inicio']).date() if isinstance(evento['fecha_inicio'], str) else evento['fecha_inicio']
            
            if fecha == hoy:
                hoy_list.append(EventoResponse(**_convertir_evento_response(evento)))
            elif fecha == manana:
                manana_list.append(EventoResponse(**_convertir_evento_response(evento)))
            elif fecha <= fin_semana:
                semana_list.append(EventoResponse(**_convertir_evento_response(evento)))
            elif fecha <= fin_mes:
                mes_list.append(EventoResponse(**_convertir_evento_response(evento)))
            else:
                proximos_list.append(EventoResponse(**_convertir_evento_response(evento)))
        
        return EventoProximosResponse(
            hoy=hoy_list,
            manana=manana_list,
            esta_semana=semana_list,
            este_mes=mes_list,
            proximos_meses=proximos_list
        )
        
    except Exception as e:
        logger.error(f"Error en get_eventos_proximos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hoy", response_model=List[EventoResponse])
async def get_eventos_hoy(
    supabase = Depends(get_db)
):
    """Obtener eventos que ocurren hoy."""
    try:
        evento_repo = EventoRepository(supabase)
        
        eventos = await evento_repo.get_today()
        
        return [EventoResponse(**_convertir_evento_response(e)) for e in eventos]
        
    except Exception as e:
        logger.error(f"Error en get_eventos_hoy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/semana", response_model=List[EventoResponse])
async def get_eventos_semana(
    supabase = Depends(get_db)
):
    """Obtener eventos de esta semana."""
    try:
        evento_repo = EventoRepository(supabase)
        
        eventos = await evento_repo.get_this_week()
        
        return [EventoResponse(**_convertir_evento_response(e)) for e in eventos]
        
    except Exception as e:
        logger.error(f"Error en get_eventos_semana: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mes", response_model=List[EventoResponse])
async def get_eventos_mes(
    supabase = Depends(get_db)
):
    """Obtener eventos de este mes."""
    try:
        evento_repo = EventoRepository(supabase)
        
        eventos = await evento_repo.get_this_month()
        
        return [EventoResponse(**_convertir_evento_response(e)) for e in eventos]
        
    except Exception as e:
        logger.error(f"Error en get_eventos_mes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gratis", response_model=List[EventoResponse])
async def get_eventos_gratis(
    limit: int = Query(20, ge=1, le=50, description="Número de eventos"),
    supabase = Depends(get_db)
):
    """Obtener eventos gratuitos."""
    try:
        evento_repo = EventoRepository(supabase)
        
        eventos = await evento_repo.get_gratis(limit=limit)
        
        return [EventoResponse(**_convertir_evento_response(e)) for e in eventos]
        
    except Exception as e:
        logger.error(f"Error en get_eventos_gratis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{evento_id}", response_model=EventoDetalleResponse)
async def get_evento_detalle(
    evento_id: int,
    supabase = Depends(get_db)
):
    """Obtener detalle completo de un evento específico."""
    try:
        evento_repo = EventoRepository(supabase)
        
        evento = await evento_repo.get_by_id(evento_id)
        
        if not evento:
            raise NotFoundException(
                resource_type="Evento",
                resource_id=evento_id
            )
        
        # Calcular campos adicionales
        fecha_inicio = datetime.fromisoformat(evento['fecha_inicio']).date() if isinstance(evento['fecha_inicio'], str) else evento['fecha_inicio']
        hoy = date.today()
        
        esta_activo = fecha_inicio <= hoy <= (evento.get('fecha_fin') or fecha_inicio)
        es_gratis = evento.get('precio') and 'gratis' in evento.get('precio', '').lower()
        
        return EventoDetalleResponse(
            **_convertir_evento_response(evento),
            organizador=evento.get('organizador'),
            contacto_email=evento.get('contacto_email'),
            contacto_telefono=evento.get('contacto_telefono'),
            sitio_web=evento.get('sitio_web'),
            instagram=evento.get('instagram'),
            capacidad=evento.get('capacidad'),
            imagenes=evento.get('imagenes', []),
            video_url=evento.get('video_url'),
            created_at=evento.get('created_at'),
            updated_at=evento.get('updated_at'),
            esta_activo=esta_activo,
            es_gratis=es_gratis,
            fecha_formateada=_formatear_fecha(fecha_inicio),
            horario_formateado=f"{evento.get('hora_inicio', '')} - {evento.get('hora_fin', '')}".strip(' -')
        )
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_evento_detalle: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lugar/{lugar_id}", response_model=List[EventoResponse])
async def get_eventos_por_lugar(
    lugar_id: int,
    supabase = Depends(get_db)
):
    """Obtener eventos asociados a un lugar específico."""
    try:
        evento_repo = EventoRepository(supabase)
        
        eventos = await evento_repo.get_by_multiple_fields({"lugar_id": lugar_id, "activo": True})
        
        return [EventoResponse(**_convertir_evento_response(e)) for e in eventos]
        
    except Exception as e:
        logger.error(f"Error en get_eventos_por_lugar: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/buscar/{search_term}", response_model=List[EventoResponse])
async def buscar_eventos(
    search_term: str,
    limit: int = Query(20, ge=1, le=50),
    supabase = Depends(get_db)
):
    """Buscar eventos por nombre o descripción."""
    try:
        evento_repo = EventoRepository(supabase)
        
        eventos = await evento_repo.search_eventos(search_term, limit=limit)
        
        return [EventoResponse(**_convertir_evento_response(e)) for e in eventos]
        
    except Exception as e:
        logger.error(f"Error en buscar_eventos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ENDPOINTS ADMIN (requieren autenticación)
# =====================================================

@router.post("/", response_model=EventoDetalleResponse)
async def crear_evento(
    evento_data: EventoCreateRequest,
    supabase = Depends(get_db)
    # user: dict = Depends(require_admin)  # Descomentar para producción
):
    """
    Crear un nuevo evento (solo administradores).
    """
    try:
        evento_repo = EventoRepository(supabase)
        
        # Verificar si ya existe un evento con mismo nombre y fecha
        existe = await evento_repo.exists_by_name_and_date(
            evento_data.nombre,
            evento_data.fecha_inicio
        )
        
        if existe:
            raise ValidationException(f"Ya existe un evento con nombre '{evento_data.nombre}' en esa fecha")
        
        # Crear evento
        nuevo_evento = await evento_repo.create(evento_data.model_dump(exclude_none=True))
        
        return EventoDetalleResponse(
            **_convertir_evento_response(nuevo_evento),
            created_at=nuevo_evento.get('created_at'),
            updated_at=nuevo_evento.get('updated_at'),
            esta_activo=False,
            es_gratis=False,
            fecha_formateada="",
            horario_formateado=""
        )
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en crear_evento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# INFO ENDPOINT
# =====================================================

@router.get("/info")
async def get_eventos_info():
    """Obtener información sobre el servicio de eventos."""
    return {
        "servicio": "Eventos - LoCALIzate",
        "version": "1.0.0",
        "descripcion": "Endpoints para eventos y festivales en Cali",
        "endpoints_disponibles": [
            "GET /eventos/",
            "GET /eventos/destacados",
            "GET /eventos/proximos",
            "GET /eventos/hoy",
            "GET /eventos/semana",
            "GET /eventos/mes",
            "GET /eventos/gratis",
            "GET /eventos/{id}",
            "GET /eventos/lugar/{lugar_id}",
            "GET /eventos/buscar/{termino}",
            "POST /eventos/ (admin)",
            "GET /eventos/info"
        ],
        "filtros_disponibles": [
            "destacados",
            "categoria",
            "busqueda",
            "desde",
            "hasta"
        ]
    }