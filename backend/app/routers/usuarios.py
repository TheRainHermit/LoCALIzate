"""
Endpoints para Usuarios - LoCALIzate Backend
===========================================

Proporciona endpoints para gestión de usuarios y perfiles:
    - Perfil de usuario (ver, actualizar)
    - Preferencias y configuración
    - Intereses del usuario
    - Favoritos (lugares guardados)
    - Estadísticas personales
    - Historial de actividad

Dependencias:
    - UsuarioRepository: Acceso a datos de usuarios
    - LugarRepository: Para gestión de favoritos
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
import logging

from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.lugar_repo import LugarRepository
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional, get_pagination, PaginationParams
from app.core.exceptions import NotFoundException, ValidationException

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# =====================================================
# PYDANTIC MODELS
# =====================================================

class PerfilUpdateRequest(BaseModel):
    """Request para actualizar perfil de usuario"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    telefono: Optional[str] = Field(None, max_length=50)
    ciudad_origen: Optional[str] = Field(None, max_length=100)
    pais: Optional[str] = Field(None, max_length=100)
    latitud: Optional[float] = Field(None, ge=-90, le=90)
    longitud: Optional[float] = Field(None, ge=-180, le=180)


class PreferenciasUpdateRequest(BaseModel):
    """Request para actualizar preferencias de usuario"""
    idioma: Optional[str] = Field(None, pattern="^(es|en)$")
    tema: Optional[str] = Field(None, pattern="^(light|dark|system)$")
    notificaciones_email: Optional[bool] = None
    notificaciones_push: Optional[bool] = None
    notificaciones_tipo: Optional[str] = Field(None, pattern="^(todas|solo_eventos|solo_promociones|ninguna)$")
    compartir_ubicacion: Optional[bool] = None
    perfil_publico: Optional[bool] = None


class InteresesUpdateRequest(BaseModel):
    """Request para actualizar intereses del usuario"""
    intereses: List[str] = Field(..., description="Lista de intereses")
    
    def validate_intereses(self):
        intereses_validos = ["cultura", "naturaleza", "gastronomia", "salsa", "aventura"]
        for interes in self.intereses:
            if interes not in intereses_validos:
                raise ValidationException(f"Interés inválido: {interes}. Opciones: {intereses_validos}")


class FavoritoResponse(BaseModel):
    """Respuesta de lugar favorito"""
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


class PerfilResponse(BaseModel):
    """Respuesta de perfil de usuario"""
    id: str
    email: str
    nombre: Optional[str]
    apellido: Optional[str]
    nombre_completo: str
    avatar_url: Optional[str]
    telefono: Optional[str]
    ciudad_origen: Optional[str]
    pais: Optional[str]
    intereses: List[str]
    idioma: str
    tema: str
    notificaciones_email: bool
    notificaciones_push: bool
    perfil_publico: bool
    total_rutas: int
    total_favoritos: int
    total_resenas: int
    created_at: str


class EstadisticasResponse(BaseModel):
    """Respuesta de estadísticas del usuario"""
    usuario_id: str
    total_rutas: int
    rutas_completadas: int
    tasa_completacion: float
    total_favoritos: int
    total_resenas: int
    rating_promedio: float
    intereses: List[str]
    intereses_count: int
    nivel_explorador: str
    progreso_siguiente_nivel: int
    badges: List[str] = []


class UbicacionUpdateRequest(BaseModel):
    """Request para actualizar ubicación actual"""
    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _calcular_nivel_explorador(total_lugares: int) -> tuple:
    """Calcular nivel de explorador y progreso."""
    if total_lugares >= 50:
        return "🌎 Explorador Legendario", 100
    elif total_lugares >= 30:
        progreso = int(((total_lugares - 30) / 20) * 100)
        return "🌟 Explorador Experto", min(100, progreso)
    elif total_lugares >= 15:
        progreso = int(((total_lugares - 15) / 15) * 100)
        return "⭐ Explorador Avanzado", min(100, progreso)
    elif total_lugares >= 5:
        progreso = int(((total_lugares - 5) / 10) * 100)
        return "📍 Explorador Activo", min(100, progreso)
    else:
        progreso = int((total_lugares / 5) * 100) if total_lugares > 0 else 0
        return "🚀 Nuevo Explorador", progreso


# =====================================================
# ENDPOINTS DE PERFIL
# =====================================================

@router.get("/perfil", response_model=PerfilResponse)
async def get_perfil(
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Obtener perfil del usuario autenticado.
    """
    try:
        usuario_repo = UsuarioRepository(supabase)
        
        perfil = await usuario_repo.get_profile_with_stats(user['id'])
        
        return PerfilResponse(
            id=perfil['id'],
            email=perfil.get('email', user.get('email', '')),
            nombre=perfil.get('nombre'),
            apellido=perfil.get('apellido'),
            nombre_completo=perfil.get('nombre_completo', perfil.get('nombre', 'Turista')),
            avatar_url=perfil.get('avatar_url'),
            telefono=perfil.get('telefono'),
            ciudad_origen=perfil.get('ciudad_origen'),
            pais=perfil.get('pais'),
            intereses=perfil.get('intereses', []),
            idioma=perfil.get('idioma', 'es'),
            tema=perfil.get('tema', 'light'),
            notificaciones_email=perfil.get('notificaciones_email', True),
            notificaciones_push=perfil.get('notificaciones_push', True),
            perfil_publico=perfil.get('perfil_publico', True),
            total_rutas=perfil.get('total_rutas', 0),
            total_favoritos=perfil.get('total_favoritos', 0),
            total_resenas=perfil.get('total_resenas', 0),
            created_at=perfil.get('created_at')
        )
        
    except Exception as e:
        logger.error(f"Error en get_perfil: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/perfil", response_model=PerfilResponse)
async def update_perfil(
    update_data: PerfilUpdateRequest,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Actualizar perfil del usuario autenticado.
    """
    try:
        usuario_repo = UsuarioRepository(supabase)
        
        # Filtrar campos no nulos
        data = {k: v for k, v in update_data.model_dump().items() if v is not None}
        
        if data:
            perfil = await usuario_repo.update(user['id'], data, id_column="id")
        else:
            perfil = await usuario_repo.get_profile_with_stats(user['id'])
        
        return PerfilResponse(
            id=perfil['id'],
            email=perfil.get('email', user.get('email', '')),
            nombre=perfil.get('nombre'),
            apellido=perfil.get('apellido'),
            nombre_completo=perfil.get('nombre_completo', perfil.get('nombre', 'Turista')),
            avatar_url=perfil.get('avatar_url'),
            telefono=perfil.get('telefono'),
            ciudad_origen=perfil.get('ciudad_origen'),
            pais=perfil.get('pais'),
            intereses=perfil.get('intereses', []),
            idioma=perfil.get('idioma', 'es'),
            tema=perfil.get('tema', 'light'),
            notificaciones_email=perfil.get('notificaciones_email', True),
            notificaciones_push=perfil.get('notificaciones_push', True),
            perfil_publico=perfil.get('perfil_publico', True),
            total_rutas=perfil.get('total_rutas', 0),
            total_favoritos=perfil.get('total_favoritos', 0),
            total_resenas=perfil.get('total_resenas', 0),
            created_at=perfil.get('created_at')
        )
        
    except Exception as e:
        logger.error(f"Error en update_perfil: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferencias", response_model=PreferenciasUpdateRequest)
async def get_preferencias(
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Obtener preferencias del usuario.
    """
    try:
        usuario_repo = UsuarioRepository(supabase)
        
        perfil = await usuario_repo.get_by_id(user['id'], id_column="id")
        
        if not perfil:
            raise NotFoundException(resource_type="Usuario", resource_id=user['id'])
        
        return PreferenciasUpdateRequest(
            idioma=perfil.get('idioma', 'es'),
            tema=perfil.get('tema', 'light'),
            notificaciones_email=perfil.get('notificaciones_email', True),
            notificaciones_push=perfil.get('notificaciones_push', True),
            notificaciones_tipo=perfil.get('notificaciones_tipo', 'todas'),
            compartir_ubicacion=perfil.get('compartir_ubicacion', False),
            perfil_publico=perfil.get('perfil_publico', True)
        )
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_preferencias: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/preferencias")
async def update_preferencias(
    update_data: PreferenciasUpdateRequest,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Actualizar preferencias del usuario.
    """
    try:
        usuario_repo = UsuarioRepository(supabase)
        
        data = {k: v for k, v in update_data.model_dump().items() if v is not None}
        
        if data:
            await usuario_repo.update_preferences(user['id'], data)
        
        return {"message": "Preferencias actualizadas correctamente"}
        
    except Exception as e:
        logger.error(f"Error en update_preferencias: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ENDPOINTS DE INTERESES
# =====================================================

@router.get("/intereses", response_model=List[str])
async def get_intereses(
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Obtener lista de intereses del usuario.
    """
    try:
        usuario_repo = UsuarioRepository(supabase)
        
        intereses = await usuario_repo.get_intereses(user['id'])
        
        return intereses
        
    except Exception as e:
        logger.error(f"Error en get_intereses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/intereses", response_model=List[str])
async def update_intereses(
    update_data: InteresesUpdateRequest,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Actualizar lista de intereses del usuario.
    """
    try:
        update_data.validate_intereses()
        
        usuario_repo = UsuarioRepository(supabase)
        
        intereses = await usuario_repo.set_intereses(user['id'], update_data.intereses)
        
        return intereses
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en update_intereses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intereses/{interes}", response_model=List[str])
async def agregar_interes(
    interes: str,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Agregar un interés a la lista del usuario.
    """
    intereses_validos = ["cultura", "naturaleza", "gastronomia", "salsa", "aventura"]
    
    if interes not in intereses_validos:
        raise HTTPException(status_code=400, detail=f"Interés inválido. Opciones: {intereses_validos}")
    
    try:
        usuario_repo = UsuarioRepository(supabase)
        
        intereses = await usuario_repo.add_interes(user['id'], interes)
        
        return intereses
        
    except Exception as e:
        logger.error(f"Error en agregar_interes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/intereses/{interes}", response_model=List[str])
async def eliminar_interes(
    interes: str,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Eliminar un interés de la lista del usuario.
    """
    try:
        usuario_repo = UsuarioRepository(supabase)
        
        intereses = await usuario_repo.remove_interes(user['id'], interes)
        
        return intereses
        
    except Exception as e:
        logger.error(f"Error en eliminar_interes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ENDPOINTS DE FAVORITOS
# =====================================================

@router.get("/favoritos", response_model=List[FavoritoResponse])
async def get_favoritos(
    pagination: PaginationParams = Depends(get_pagination),
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Obtener lista de lugares favoritos del usuario.
    """
    try:
        usuario_repo = UsuarioRepository(supabase)
        
        favoritos = await usuario_repo.get_favoritos(
            user['id'],
            limit=pagination.limit,
            offset=pagination.offset
        )
        
        return [
            FavoritoResponse(
                id=f['id'],
                nombre=f.get('nombre', ''),
                descripcion_corta=f.get('descripcion_corta'),
                latitud=f.get('lat', f.get('latitud', 0)),
                longitud=f.get('lng', f.get('longitud', 0)),
                direccion=f.get('direccion'),
                interes=f.get('interes', 'general'),
                icono=f.get('icono', '📍'),
                rating=f.get('rating', 0),
                imagen=f.get('imagen', f.get('imagen_principal')),
                fecha_agregado=f.get('fecha_agregado', datetime.now().isoformat())
            )
            for f in favoritos
        ]
        
    except Exception as e:
        logger.error(f"Error en get_favoritos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/favoritos/{lugar_id}")
async def agregar_favorito(
    lugar_id: int,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Agregar un lugar a favoritos.
    """
    try:
        usuario_repo = UsuarioRepository(supabase)
        lugar_repo = LugarRepository(supabase)
        
        # Verificar que el lugar existe
        lugar = await lugar_repo.get_by_id(lugar_id)
        if not lugar:
            raise NotFoundException(resource_type="Lugar", resource_id=lugar_id)
        
        agregado = await usuario_repo.add_favorito(user['id'], lugar_id)
        
        if agregado:
            return {"message": f"Lugar '{lugar.get('nombre')}' agregado a favoritos", "lugar_id": lugar_id}
        else:
            return {"message": "El lugar ya estaba en favoritos", "lugar_id": lugar_id}
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en agregar_favorito: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/favoritos/{lugar_id}")
async def eliminar_favorito(
    lugar_id: int,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Eliminar un lugar de favoritos.
    """
    try:
        usuario_repo = UsuarioRepository(supabase)
        
        eliminado = await usuario_repo.remove_favorito(user['id'], lugar_id)
        
        if eliminado:
            return {"message": "Lugar eliminado de favoritos", "lugar_id": lugar_id}
        else:
            raise NotFoundException(resource_type="Favorito", resource_id=lugar_id)
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en eliminar_favorito: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/favoritos/check/{lugar_id}")
async def check_favorito(
    lugar_id: int,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Verificar si un lugar está en favoritos.
    """
    try:
        usuario_repo = UsuarioRepository(supabase)
        
        es_favorito = await usuario_repo.is_favorito(user['id'], lugar_id)
        
        return {"lugar_id": lugar_id, "es_favorito": es_favorito}
        
    except Exception as e:
        logger.error(f"Error en check_favorito: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ENDPOINTS DE ESTADÍSTICAS
# =====================================================

@router.get("/estadisticas", response_model=EstadisticasResponse)
async def get_estadisticas(
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Obtener estadísticas y métricas del usuario.
    """
    try:
        usuario_repo = UsuarioRepository(supabase)
        
        stats = await usuario_repo.get_user_stats(user['id'])
        
        nivel, progreso = _calcular_nivel_explorador(stats.get('total_lugares_visitados', 0))
        
        # Badges simulados (en producción vendrían de DB)
        badges = []
        if stats.get('total_rutas', 0) >= 5:
            badges.append("🗺️ Planificador")
        if stats.get('total_favoritos', 0) >= 10:
            badges.append("❤️ Coleccionista")
        if stats.get('total_resenas', 0) >= 3:
            badges.append("✍️ Crítico")
        if stats.get('rutas_completadas', 0) >= 3:
            badges.append("🏁 Completador")
        
        return EstadisticasResponse(
            usuario_id=user['id'],
            total_rutas=stats.get('total_rutas', 0),
            rutas_completadas=stats.get('rutas_completadas', 0),
            tasa_completacion=round((stats.get('rutas_completadas', 0) / max(1, stats.get('total_rutas', 0)) * 100), 1),
            total_favoritos=stats.get('total_favoritos', 0),
            total_resenas=stats.get('total_resenas', 0),
            rating_promedio=stats.get('rating_promedio', 0),
            intereses=stats.get('intereses', []),
            intereses_count=stats.get('intereses_count', 0),
            nivel_explorador=nivel,
            progreso_siguiente_nivel=progreso,
            badges=badges
        )
        
    except Exception as e:
        logger.error(f"Error en get_estadisticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ENDPOINTS DE UBICACIÓN
# =====================================================

@router.put("/ubicacion")
async def actualizar_ubicacion(
    ubicacion: UbicacionUpdateRequest,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Actualizar ubicación actual del usuario (para funciones de proximidad).
    """
    try:
        usuario_repo = UsuarioRepository(supabase)
        
        await usuario_repo.update_preferences(
            user['id'],
            {"latitud": ubicacion.latitud, "longitud": ubicacion.longitud}
        )
        
        return {
            "message": "Ubicación actualizada correctamente",
            "latitud": ubicacion.latitud,
            "longitud": ubicacion.longitud
        }
        
    except Exception as e:
        logger.error(f"Error en actualizar_ubicacion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ubicacion")
async def get_ubicacion(
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Obtener ubicación actual del usuario.
    """
    try:
        usuario_repo = UsuarioRepository(supabase)
        
        perfil = await usuario_repo.get_by_id(user['id'], id_column="id")
        
        if not perfil:
            raise NotFoundException(resource_type="Usuario", resource_id=user['id'])
        
        return {
            "latitud": perfil.get('latitud'),
            "longitud": perfil.get('longitud'),
            "actualizada": perfil.get('updated_at')
        }
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_ubicacion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# INFO ENDPOINT
# =====================================================

@router.get("/info")
async def get_usuarios_info():
    """Obtener información sobre el servicio de usuarios."""
    return {
        "servicio": "Usuarios - LoCALIzate",
        "version": "1.0.0",
        "descripcion": "Endpoints para gestión de perfiles y preferencias de usuario",
        "endpoints_disponibles": [
            "GET /usuarios/perfil",
            "PUT /usuarios/perfil",
            "GET /usuarios/preferencias",
            "PUT /usuarios/preferencias",
            "GET /usuarios/intereses",
            "PUT /usuarios/intereses",
            "POST /usuarios/intereses/{interes}",
            "DELETE /usuarios/intereses/{interes}",
            "GET /usuarios/favoritos",
            "POST /usuarios/favoritos/{lugar_id}",
            "DELETE /usuarios/favoritos/{lugar_id}",
            "GET /usuarios/favoritos/check/{lugar_id}",
            "GET /usuarios/estadisticas",
            "PUT /usuarios/ubicacion",
            "GET /usuarios/ubicacion",
            "GET /usuarios/info"
        ],
        "intereses_disponibles": ["cultura", "naturaleza", "gastronomia", "salsa", "aventura"],
        "temas_disponibles": ["light", "dark", "system"],
        "idiomas_disponibles": ["es", "en"]
    }