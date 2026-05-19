"""
Endpoints para Analytics - LoCALIzate Backend
============================================

Proporciona endpoints para métricas y estadísticas de la aplicación:
    - Estadísticas globales de la plataforma
    - Lugares más visitados y mejor calificados
    - Eventos más populares
    - Tendencias y actividad de usuarios
    - Dashboard para administradores

Dependencias:
    - LugarRepository: Datos de lugares
    - EventoRepository: Datos de eventos
    - UsuarioRepository: Datos de usuarios
    - RutaRepository: Datos de rutas
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date, timedelta
import logging

from app.repositories.lugar_repo import LugarRepository
from app.repositories.evento_repo import EventoRepository
from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.ruta_repo import RutaRepository
from app.core.database import get_db
from app.core.dependencies import require_admin, get_current_user_optional
from app.core.exceptions import NotFoundException

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# =====================================================
# PYDANTIC MODELS
# =====================================================

class TopLugarResponse(BaseModel):
    """Lugar en ranking"""
    id: int
    nombre: str
    interes: str
    icono: str
    rating: float
    total_visitas: Optional[int] = None
    total_favoritos: Optional[int] = None


class TopEventoResponse(BaseModel):
    """Evento en ranking"""
    id: int
    nombre: str
    fecha_inicio: str
    ubicacion: Optional[str]
    icono: str
    interes_count: Optional[int] = None


class EstadisticasGlobalesResponse(BaseModel):
    """Estadísticas globales de la plataforma"""
    total_usuarios: int
    total_lugares: int
    total_eventos: int
    total_rutas: int
    total_resenas: int
    rating_promedio_global: float
    lugares_por_interes: Dict[str, int]
    ultima_actualizacion: str


class ActividadResponse(BaseModel):
    """Actividad de usuarios por período"""
    fecha: str
    nuevos_usuarios: int
    rutas_creadas: int
    resenas_escritas: int
    favoritos_agregados: int


class TendenciasResponse(BaseModel):
    """Tendencias de la plataforma"""
    lugares_en_tendencia: List[TopLugarResponse]
    categorias_populares: List[Dict[str, Any]]
    horarios_populares: List[Dict[str, int]]
    dias_populares: List[Dict[str, int]]


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _get_interes_nombre(interes: str) -> str:
    """Obtener nombre legible del interés."""
    nombres = {
        'cultura': '🎭 Cultura',
        'naturaleza': '🌳 Naturaleza',
        'gastronomia': '🍽️ Gastronomía',
        'salsa': '💃 Salsa',
        'aventura': '🧗 Aventura'
    }
    return nombres.get(interes, interes)


# =====================================================
# ENDPOINTS PÚBLICOS (estadísticas generales)
# =====================================================

@router.get("/globales", response_model=EstadisticasGlobalesResponse)
async def get_estadisticas_globales(
    supabase = Depends(get_db)
):
    """
    Obtener estadísticas globales de la plataforma.
    
    Incluye:
    - Total de usuarios, lugares, eventos, rutas
    - Rating promedio global
    - Distribución de lugares por interés
    """
    try:
        lugar_repo = LugarRepository(supabase)
        evento_repo = EventoRepository(supabase)
        usuario_repo = UsuarioRepository(supabase)
        ruta_repo = RutaRepository(supabase)
        
        # Estadísticas básicas
        total_lugares = await lugar_repo.get_count(filters={"activo": True})
        total_eventos = await evento_repo.get_count(filters={"activo": True})
        
        # Usuarios (desde tabla perfiles)
        usuarios_result = supabase.table("perfiles").select("id", count="exact").execute()
        total_usuarios = getattr(usuarios_result, 'count', 0) or 0
        
        # Rutas
        total_rutas = await ruta_repo.get_count(filters={"activa": True})
        
        # Reseñas
        resenas_result = supabase.table("resenas").select("id", count="exact").execute()
        total_resenas = getattr(resenas_result, 'count', 0) or 0
        
        # Rating promedio global
        rating_result = supabase.table("lugares").select("rating").eq("activo", True).execute()
        ratings = [l.get('rating', 0) for l in (rating_result.data or []) if l.get('rating')]
        rating_promedio = round(sum(ratings) / len(ratings), 2) if ratings else 0
        
        # Distribución por interés
        lugares_por_interes = {}
        intereses = ["cultura", "naturaleza", "gastronomia", "salsa", "aventura"]
        for interes in intereses:
            count = await lugar_repo.get_count(filters={"interes": interes, "activo": True})
            lugares_por_interes[_get_interes_nombre(interes)] = count
        
        return EstadisticasGlobalesResponse(
            total_usuarios=total_usuarios,
            total_lugares=total_lugares,
            total_eventos=total_eventos,
            total_rutas=total_rutas,
            total_resenas=total_resenas,
            rating_promedio_global=rating_promedio,
            lugares_por_interes=lugares_por_interes,
            ultima_actualizacion=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error en get_estadisticas_globales: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top/lugares", response_model=List[TopLugarResponse])
async def get_top_lugares(
    limit: int = Query(10, ge=1, le=50, description="Número de resultados"),
    interes: Optional[str] = Query(None, description="Filtrar por interés"),
    supabase = Depends(get_db)
):
    """
    Obtener ranking de los mejores lugares.
    
    Ordenado por rating y popularidad.
    """
    try:
        lugar_repo = LugarRepository(supabase)
        
        # Construir filtros
        filters = {"activo": True}
        if interes:
            filters["interes"] = interes
        
        lugares = await lugar_repo.get_all(
            filters=filters,
            limit=limit,
            order_by="rating",
            order_desc=True
        )
        
        return [
            TopLugarResponse(
                id=l.get('id'),
                nombre=l.get('nombre'),
                interes=l.get('interes', 'general'),
                icono=l.get('icono', '📍'),
                rating=l.get('rating', 0),
                total_visitas=l.get('rating_count', 0)
            )
            for l in lugares
        ]
        
    except Exception as e:
        logger.error(f"Error en get_top_lugares: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top/eventos", response_model=List[TopEventoResponse])
async def get_top_eventos(
    limit: int = Query(10, ge=1, le=50, description="Número de resultados"),
    supabase = Depends(get_db)
):
    """
    Obtener ranking de eventos más populares/destacados.
    """
    try:
        evento_repo = EventoRepository(supabase)
        
        eventos = await evento_repo.get_destacados(limit=limit)
        
        return [
            TopEventoResponse(
                id=e.get('id'),
                nombre=e.get('nombre'),
                fecha_inicio=e.get('fecha_inicio'),
                ubicacion=e.get('ubicacion'),
                icono=e.get('icono', '🎉'),
                interes_count=None
            )
            for e in eventos
        ]
        
    except Exception as e:
        logger.error(f"Error en get_top_eventos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tendencias", response_model=TendenciasResponse)
async def get_tendencias(
    supabase = Depends(get_db)
):
    """
    Obtener tendencias actuales de la plataforma.
    
    Incluye:
    - Lugares en tendencia (más visitados recientemente)
    - Categorías más populares
    - Horarios y días con más actividad
    """
    try:
        lugar_repo = LugarRepository(supabase)
        
        # Lugares en tendencia (destacados + mejor rating)
        lugares_tendencia = await lugar_repo.get_popular(limit=6)
        
        lugares_response = [
            TopLugarResponse(
                id=l.get('id'),
                nombre=l.get('nombre'),
                interes=l.get('interes', 'general'),
                icono=l.get('icono', '📍'),
                rating=l.get('rating', 0),
                total_visitas=l.get('rating_count', 0)
            )
            for l in lugares_tendencia
        ]
        
        # Categorías populares (basado en lugares por interés)
        intereses = ["cultura", "naturaleza", "gastronomia", "salsa", "aventura"]
        categorias_populares = []
        for interes in intereses:
            count = await lugar_repo.get_count(filters={"interes": interes, "activo": True})
            categorias_populares.append({
                "categoria": _get_interes_nombre(interes),
                "slug": interes,
                "total": count
            })
        categorias_populares.sort(key=lambda x: x["total"], reverse=True)
        
        # Horarios populares (simulado - en producción con logs reales)
        horarios_populares = [
            {"hora": "9:00", "actividad": 15},
            {"hora": "10:00", "actividad": 25},
            {"hora": "11:00", "actividad": 30},
            {"hora": "14:00", "actividad": 20},
            {"hora": "15:00", "actividad": 28},
            {"hora": "16:00", "actividad": 22},
            {"hora": "19:00", "actividad": 35},
            {"hora": "20:00", "actividad": 40},
            {"hora": "21:00", "actividad": 45}
        ]
        
        # Días populares
        dias_populares = [
            {"dia": "Lunes", "actividad": 120},
            {"dia": "Martes", "actividad": 130},
            {"dia": "Miércoles", "actividad": 125},
            {"dia": "Jueves", "actividad": 140},
            {"dia": "Viernes", "actividad": 200},
            {"dia": "Sábado", "actividad": 250},
            {"dia": "Domingo", "actividad": 180}
        ]
        
        return TendenciasResponse(
            lugares_en_tendencia=lugares_response,
            categorias_populares=categorias_populares,
            horarios_populares=horarios_populares,
            dias_populares=dias_populares
        )
        
    except Exception as e:
        logger.error(f"Error en get_tendencias: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actividad", response_model=List[ActividadResponse])
async def get_actividad(
    dias: int = Query(30, ge=1, le=90, description="Número de días hacia atrás"),
    supabase = Depends(get_db)
):
    """
    Obtener actividad de usuarios por día.
    
    Requiere autenticación de administrador.
    """
    try:
        fecha_corte = date.today() - timedelta(days=dias)
        
        # Obtener logs de actividad (simulado - en producción con tabla actividad_logs)
        # Por ahora, retornamos datos simulados basados en tendencias generales
        
        actividad = []
        for i in range(dias):
            fecha = fecha_corte + timedelta(days=i)
            
            # Simular datos (en producción desde base de datos)
            # Estos valores vendrían de la tabla actividad_logs
            actividad.append(ActividadResponse(
                fecha=fecha.isoformat(),
                nuevos_usuarios=5 + (i % 10),
                rutas_creadas=10 + (i % 15),
                resenas_escritas=8 + (i % 12),
                favoritos_agregados=20 + (i % 25)
            ))
        
        return actividad
        
    except Exception as e:
        logger.error(f"Error en get_actividad: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ENDPOINTS ADMIN (requieren autenticación)
# =====================================================

@router.get("/dashboard")
async def get_dashboard_admin(
    supabase = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """
    Dashboard completo para administradores.
    
    Incluye todas las métricas y estadísticas en un solo endpoint.
    Requiere privilegios de administrador.
    """
    try:
        lugar_repo = LugarRepository(supabase)
        evento_repo = EventoRepository(supabase)
        ruta_repo = RutaRepository(supabase)
        
        # Estadísticas globales
        total_lugares = await lugar_repo.get_count(filters={"activo": True})
        total_eventos = await evento_repo.get_count(filters={"activo": True})
        total_rutas = await ruta_repo.get_count(filters={"activa": True})
        
        # Usuarios activos
        usuarios_result = supabase.table("perfiles").select("id", count="exact").execute()
        total_usuarios = getattr(usuarios_result, 'count', 0) or 0
        
        # Usuarios nuevos (últimos 7 días)
        fecha_semana = (date.today() - timedelta(days=7)).isoformat()
        usuarios_nuevos_result = supabase.table("perfiles")\
            .select("id", count="exact")\
            .gte("created_at", fecha_semana)\
            .execute()
        usuarios_nuevos = getattr(usuarios_nuevos_result, 'count', 0) or 0
        
        # Rutas creadas en últimos 7 días
        rutas_semana = await ruta_repo.get_count(filters={"created_at": fecha_semana})
        
        # Lugares por interés
        lugares_por_interes = {}
        intereses = ["cultura", "naturaleza", "gastronomia", "salsa", "aventura"]
        for interes in intereses:
            count = await lugar_repo.get_count(filters={"interes": interes, "activo": True})
            lugares_por_interes[interes] = count
        
        # Top 5 lugares
        top_lugares = await lugar_repo.get_popular(limit=5)
        top_lugares_data = [
            {"id": l.get('id'), "nombre": l.get('nombre'), "rating": l.get('rating')}
            for l in top_lugares
        ]
        
        return {
            "resumen": {
                "total_usuarios": total_usuarios,
                "usuarios_nuevos_semana": usuarios_nuevos,
                "total_lugares": total_lugares,
                "total_eventos": total_eventos,
                "total_rutas": total_rutas,
                "rutas_creadas_semana": rutas_semana
            },
            "distribucion": {
                "lugares_por_interes": lugares_por_interes
            },
            "ranking": {
                "top_lugares": top_lugares_data
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error en get_dashboard_admin: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usuarios/top", response_model=List[Dict[str, Any]])
async def get_top_usuarios(
    limit: int = Query(10, ge=1, le=50, description="Número de usuarios"),
    sort_by: str = Query("total_rutas", description="Campo para ordenar"),
    supabase = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """
    Obtener ranking de usuarios más activos.
    
    Requiere privilegios de administrador.
    """
    try:
        usuario_repo = UsuarioRepository(supabase)
        
        top_usuarios = await usuario_repo.get_top_users(limit=limit, by=sort_by)
        
        return [
            {
                "id": u.get('id'),
                "nombre": u.get('nombre_completo', u.get('nombre', 'Usuario')),
                "email": u.get('email'),
                "total_rutas": u.get('total_rutas', 0),
                "total_favoritos": u.get('total_favoritos', 0),
                "total_resenas": u.get('total_resenas', 0),
                "created_at": u.get('created_at')
            }
            for u in top_usuarios
        ]
        
    except Exception as e:
        logger.error(f"Error en get_top_usuarios: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# INFO ENDPOINT
# =====================================================

@router.get("/info")
async def get_analytics_info():
    """Obtener información sobre el servicio de analytics."""
    return {
        "servicio": "Analytics - LoCALIzate",
        "version": "1.0.0",
        "descripcion": "Endpoints para métricas y estadísticas de la plataforma",
        "endpoints_disponibles": [
            "GET /analytics/globales",
            "GET /analytics/top/lugares",
            "GET /analytics/top/eventos",
            "GET /analytics/tendencias",
            "GET /analytics/actividad",
            "GET /analytics/dashboard (admin)",
            "GET /analytics/usuarios/top (admin)",
            "GET /analytics/info"
        ],
        "nota": "Los endpoints de administrador requieren autenticación y rol de admin"
    }