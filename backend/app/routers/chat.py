"""
Endpoints para Asistente Virtual (Chat) - LoCALIzate Backend
============================================================

Proporciona endpoints para el chatbot turístico inteligente:
    - Procesamiento de mensajes con detección de intenciones
    - Recomendaciones personalizadas de lugares
    - Historial de conversaciones por usuario
    - Sugerencias de preguntas relacionadas

Dependencias:
    - AsistenteLoCALIzate: Lógica de IA y detección de intenciones
    - LugarRepository: Acceso a datos para recomendaciones
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from app.services.asistente_ia import asistente, AsistenteLoCALIzate, RespuestaIA
from app.repositories.lugar_repo import LugarRepository
from app.repositories.chat_repo import ChatRepository
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional
from app.core.exceptions import ValidationException, NotFoundException

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat - Asistente Virtual"])


# =====================================================
# PYDANTIC MODELS
# =====================================================

class MensajeRequest(BaseModel):
    """Request para enviar un mensaje al asistente"""
    mensaje: str = Field(..., min_length=1, max_length=2000, description="Mensaje del usuario")
    conversacion_id: Optional[int] = Field(None, description="ID de conversación existente")
    user_lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitud actual del usuario")
    user_lng: Optional[float] = Field(None, ge=-180, le=180, description="Longitud actual del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mensaje": "¿Dónde puedo bailar salsa en Cali?",
                "conversacion_id": None,
                "user_lat": 3.4516,
                "user_lng": -76.5320
            }
        }


class LugarRecomendadoResponse(BaseModel):
    """Lugar recomendado en respuesta del chat"""
    id: int
    nombre: str
    rating: float
    interes: str
    icono: str
    distancia_km: Optional[float] = None


class ChatResponse(BaseModel):
    """Respuesta completa del asistente"""
    respuesta: str
    intencion: Optional[str] = None
    sugerencias: List[str] = []
    lugares_recomendados: List[LugarRecomendadoResponse] = []
    conversacion_id: int
    confianza: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ConversacionResponse(BaseModel):
    """Respuesta para historial de conversación"""
    id: int
    titulo: str
    created_at: str
    updated_at: str
    mensaje_count: int
    ultimo_mensaje: Optional[str] = None
    ultimo_mensaje_fecha: Optional[str] = None


class MensajeHistorialResponse(BaseModel):
    """Mensaje individual en el historial"""
    id: int
    rol: str
    contenido: str
    intencion: Optional[str] = None
    created_at: str


class ConversacionDetalleResponse(BaseModel):
    """Conversación completa con todos los mensajes"""
    id: int
    titulo: str
    usuario_id: str
    created_at: str
    updated_at: str
    mensajes: List[MensajeHistorialResponse]


class SugerenciaResponse(BaseModel):
    """Sugerencias de preguntas para el usuario"""
    preguntas: List[str]
    categoria: Optional[str] = None


# =====================================================
# HELPER FUNCTIONS
# =====================================================

async def _obtener_lugares_con_distancia(
    lugar_repo: LugarRepository,
    lugares_data: List[Dict],
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None
) -> List[LugarRecomendadoResponse]:
    """Obtener lugares recomendados con distancia opcional."""
    from app.services.optimizador_rutas import calcular_distancia_haversine
    
    resultados = []
    
    for lugar_data in lugares_data:
        lugar_id = lugar_data.get('id')
        if lugar_id:
            # Intentar obtener lugar completo de la BD
            lugar_completo = await lugar_repo.get_by_id(lugar_id)
            if lugar_completo:
                distancia = None
                if user_lat is not None and user_lng is not None:
                    lugar_lat = lugar_completo.get('lat', lugar_completo.get('latitud', 0))
                    lugar_lng = lugar_completo.get('lng', lugar_completo.get('longitud', 0))
                    distancia = round(calcular_distancia_haversine(
                        user_lat, user_lng, lugar_lat, lugar_lng
                    ), 2)
                
                resultados.append(LugarRecomendadoResponse(
                    id=lugar_completo.get('id'),
                    nombre=lugar_completo.get('nombre'),
                    rating=lugar_completo.get('rating', 0),
                    interes=lugar_completo.get('interes', 'general'),
                    icono=lugar_completo.get('icono', '📍'),
                    distancia_km=distancia
                ))
    
    return resultados


# =====================================================
# ENDPOINTS
# =====================================================

@router.post("/mensaje", response_model=ChatResponse)
async def procesar_mensaje(
    request: MensajeRequest,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user_optional)
):
    """
    Procesar un mensaje del usuario y obtener respuesta del asistente virtual.
    
    - Detecta automáticamente la intención del mensaje
    - Genera respuesta contextual
    - Recomienda lugares relacionados
    - Sugiere preguntas de seguimiento
    - Mantiene historial de conversación (si usuario autenticado)
    """
    try:
        # Inicializar repositorios
        lugar_repo = LugarRepository(supabase)
        chat_repo = ChatRepository(supabase)
        
        # Procesar mensaje con el asistente
        resultado: RespuestaIA = asistente.procesar_mensaje(request.mensaje)
        
        # Gestionar conversación
        conversacion_id = request.conversacion_id
        user_id = user.get('id') if user else None
        
        if user_id:
            # Usuario autenticado: guardar en historial
            if not conversacion_id:
                # Crear nueva conversación
                conv = await chat_repo.create_conversacion(
                    usuario_id=user_id,
                    titulo=request.mensaje[:50]
                )
                conversacion_id = conv['id']
            
            # Guardar mensaje del usuario
            await chat_repo.add_mensaje(
                conversacion_id=conversacion_id,
                rol="user",
                contenido=request.mensaje,
                intencion=resultado.intencion.value if resultado.intencion else None
            )
            
            # Guardar respuesta del asistente
            await chat_repo.add_mensaje(
                conversacion_id=conversacion_id,
                rol="assistant",
                contenido=resultado.texto,
                intencion=resultado.intencion.value if resultado.intencion else None,
                lugares_referenciados=[l.get('id') for l in resultado.lugares_recomendados if l.get('id')]
            )
        
        # Obtener lugares recomendados con distancias
        lugares_con_distancia = await _obtener_lugares_con_distancia(
            lugar_repo,
            resultado.lugares_recomendados,
            request.user_lat,
            request.user_lng
        )
        
        return ChatResponse(
            respuesta=resultado.texto,
            intencion=resultado.intencion.value if resultado.intencion else None,
            sugerencias=resultado.sugerencias[:5],  # Limitar a 5 sugerencias
            lugares_recomendados=lugares_con_distancia,
            conversacion_id=conversacion_id or 0,
            confianza=resultado.confianza
        )
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en procesar_mensaje: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando mensaje: {str(e)}")


@router.post("/recomendar", response_model=List[LugarRecomendadoResponse])
async def recomendar_lugares_por_mensaje(
    mensaje: str = Query(..., min_length=1, description="Mensaje del usuario para análisis"),
    limit: int = Query(5, ge=1, le=10, description="Máximo número de recomendaciones"),
    user_lat: Optional[float] = Query(None, description="Latitud del usuario"),
    user_lng: Optional[float] = Query(None, description="Longitud del usuario"),
    supabase = Depends(get_db)
):
    """
    Recomendar lugares basado en el mensaje del usuario.
    
    Útil para integraciones donde solo se necesitan recomendaciones
    sin la respuesta textual completa del asistente.
    """
    try:
        lugar_repo = LugarRepository(supabase)
        
        # Procesar mensaje para obtener intención
        resultado = asistente.procesar_mensaje(mensaje)
        
        # Obtener lugares recomendados
        lugares_con_distancia = await _obtener_lugares_con_distancia(
            lugar_repo,
            resultado.lugares_recomendados[:limit],
            user_lat,
            user_lng
        )
        
        return lugares_con_distancia
        
    except Exception as e:
        logger.error(f"Error en recomendar_lugares_por_mensaje: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sugerencias", response_model=SugerenciaResponse)
async def obtener_sugerencias(
    categoria: Optional[str] = Query(None, description="Categoría específica (salsa, comida, cultura, naturaleza)")
):
    """
    Obtener sugerencias de preguntas que el usuario puede hacer.
    
    Si se especifica una categoría, devuelve preguntas relacionadas.
    """
    sugerencias_por_categoria = {
        "salsa": [
            "¿Dónde puedo bailar salsa en Cali?",
            "¿Cuáles son las mejores discotecas de salsa?",
            "¿Hay clases de salsa para principiantes?"
        ],
        "comida": [
            "¿Dónde comer marranitas en Cali?",
            "¿Cuál es el mejor restaurante de comida típica?",
            "¿Dónde puedo probar cholado?"
        ],
        "cultura": [
            "¿Qué lugares culturales debo visitar?",
            "¿Cuál es la historia del Cristo Rey?",
            "¿Qué museos hay en Cali?"
        ],
        "naturaleza": [
            "¿Cómo llegar al Río Pance?",
            "¿Qué horario tiene el Zoológico de Cali?",
            "¿Puedo hacer senderismo en los Farallones?"
        ],
        "rutas": [
            "¿Cómo planificar una ruta por el centro?",
            "¿Qué lugares visitar en un día?",
            "¿Cómo llego de Cristo Rey al Gato del Río?"
        ],
        "eventos": [
            "¿Cuándo es la próxima Feria de Cali?",
            "¿Qué eventos hay este mes?",
            "¿Dónde comprar boletas para el Festival de Salsa?"
        ]
    }
    
    if categoria and categoria in sugerencias_por_categoria:
        return SugerenciaResponse(
            preguntas=sugerencias_por_categoria[categoria],
            categoria=categoria
        )
    
    # Sugerencias generales
    todas_preguntas = []
    for preguntas in sugerencias_por_categoria.values():
        todas_preguntas.extend(preguntas)
    
    return SugerenciaResponse(
        preguntas=todas_preguntas[:10],
        categoria=None
    )


@router.get("/conversaciones", response_model=List[ConversacionResponse])
async def get_conversaciones_usuario(
    user: dict = Depends(get_current_user),
    supabase = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Obtener historial de conversaciones del usuario autenticado.
    """
    try:
        chat_repo = ChatRepository(supabase)
        
        conversaciones = await chat_repo.get_user_conversaciones(
            usuario_id=user['id'],
            limit=limit,
            offset=offset,
            include_message_count=True
        )
        
        return [
            ConversacionResponse(
                id=c['id'],
                titulo=c.get('titulo', 'Conversación'),
                created_at=c['created_at'],
                updated_at=c.get('updated_at', c['created_at']),
                mensaje_count=c.get('mensaje_count', 0),
                ultimo_mensaje=c.get('ultimo_mensaje'),
                ultimo_mensaje_fecha=c.get('ultimo_mensaje_fecha')
            )
            for c in conversaciones
        ]
        
    except Exception as e:
        logger.error(f"Error en get_conversaciones_usuario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversaciones/{conversacion_id}", response_model=ConversacionDetalleResponse)
async def get_conversacion_detalle(
    conversacion_id: int,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_db)
):
    """
    Obtener detalle completo de una conversación con todos los mensajes.
    """
    try:
        chat_repo = ChatRepository(supabase)
        
        conversacion = await chat_repo.get_conversacion_completa(
            conversacion_id=conversacion_id,
            usuario_id=user['id']
        )
        
        return ConversacionDetalleResponse(
            id=conversacion['id'],
            titulo=conversacion.get('titulo', 'Conversación'),
            usuario_id=conversacion['usuario_id'],
            created_at=conversacion['created_at'],
            updated_at=conversacion.get('updated_at', conversacion['created_at']),
            mensajes=[
                MensajeHistorialResponse(
                    id=m['id'],
                    rol=m['rol'],
                    contenido=m['contenido'],
                    intencion=m.get('intencion'),
                    created_at=m['created_at']
                )
                for m in conversacion.get('mensajes', [])
            ]
        )
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_conversacion_detalle: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversaciones/{conversacion_id}")
async def eliminar_conversacion(
    conversacion_id: int,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_db)
):
    """
    Eliminar una conversación (borrado lógico o físico).
    """
    try:
        chat_repo = ChatRepository(supabase)
        
        eliminado = await chat_repo.delete_conversacion(
            conversacion_id=conversacion_id,
            usuario_id=user['id'],
            delete_messages=True
        )
        
        if not eliminado:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        return {"message": "Conversación eliminada correctamente", "conversacion_id": conversacion_id}
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en eliminar_conversacion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estadisticas")
async def get_estadisticas_chat(
    user: dict = Depends(get_current_user),
    supabase = Depends(get_db)
):
    """
    Obtener estadísticas de uso del chat para el usuario.
    """
    try:
        chat_repo = ChatRepository(supabase)
        
        stats = await chat_repo.get_conversation_stats(user['id'])
        
        return stats
        
    except Exception as e:
        logger.error(f"Error en get_estadisticas_chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_chat_info():
    """Obtener información sobre el asistente virtual."""
    stats = asistente.obtener_estadisticas()
    
    return {
        "servicio": "Asistente Virtual - LoCALIzate",
        "version": "2.0.0",
        "descripcion": "Chatbot turístico inteligente para consultas sobre Cali",
        "estadisticas": stats,
        "endpoints_disponibles": [
            "POST /chat/mensaje",
            "POST /chat/recomendar",
            "GET /chat/sugerencias",
            "GET /chat/conversaciones",
            "GET /chat/conversaciones/{id}",
            "DELETE /chat/conversaciones/{id}",
            "GET /chat/estadisticas",
            "GET /chat/info"
        ]
    }