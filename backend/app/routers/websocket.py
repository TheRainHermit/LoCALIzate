"""
WebSocket Router for LoCALIzate Backend
======================================

Maneja conexiones WebSocket para funcionalidades en tiempo real:
    - Chat en vivo con el asistente virtual
    - Actualización de ubicación en tiempo real
    - Lugares cercanos en tiempo real
    - Notificaciones push
    - Broadcasting de eventos

Dependencias:
    - AsistenteLoCALIzate: Procesamiento de mensajes
    - ARService: Cálculos de proximidad
    - ConnectionManager: Gestión de conexiones activas
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, List, Optional, Any
import json
import logging
from datetime import datetime

from app.services.asistente_ia import asistente
from app.services.ar_service import ar_service
from app.services.optimizador_rutas import calcular_distancia_haversine
from app.repositories.lugar_repo import LugarRepository
from app.repositories.chat_repo import ChatRepository
from app.core.database import get_db
from app.core.dependencies import get_current_user_optional

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


# =====================================================
# CONNECTION MANAGER
# =====================================================

class ConnectionManager:
    """
    Gestiona todas las conexiones WebSocket activas.
    Permite enviar mensajes a usuarios específicos o a todos.
    """
    
    def __init__(self):
        """Inicializar manager de conexiones."""
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_locations: Dict[str, Dict[str, float]] = {}
        self.user_supabase = None  # Se setea cuando hay db
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        """
        Registrar una nueva conexión WebSocket.
        
        Args:
            websocket: Conexión WebSocket
            user_id: ID del usuario (opcional, para autenticados)
        """
        await websocket.accept()
        
        key = user_id if user_id else "anonymous"
        if key not in self.active_connections:
            self.active_connections[key] = []
        self.active_connections[key].append(websocket)
        
        logger.info(f"WebSocket conectado: {key} (total: {self._count_connections()})")
    
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        """
        Remover una conexión WebSocket.
        
        Args:
            websocket: Conexión a remover
            user_id: ID del usuario (opcional)
        """
        key = user_id if user_id else "anonymous"
        if key in self.active_connections:
            self.active_connections[key].remove(websocket)
            if not self.active_connections[key]:
                del self.active_connections[key]
                # Limpiar ubicación si no hay más conexiones
                if key in self.user_locations:
                    del self.user_locations[key]
        
        logger.info(f"WebSocket desconectado: {key} (total: {self._count_connections()})")
    
    def _count_connections(self) -> int:
        """Contar total de conexiones activas."""
        return sum(len(conns) for conns in self.active_connections.values())
    
    async def send_personal(self, message: Dict, user_id: str):
        """
        Enviar mensaje a un usuario específico.
        
        Args:
            message: Mensaje a enviar
            user_id: ID del usuario destino
        """
        key = user_id
        if key in self.active_connections:
            for connection in self.active_connections[key]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error enviando mensaje a {user_id}: {str(e)}")
    
    async def broadcast(self, message: Dict, exclude_user: str = None):
        """
        Enviar mensaje a todos los usuarios conectados.
        
        Args:
            message: Mensaje a enviar
            exclude_user: Usuario a excluir (opcional)
        """
        for key, connections in self.active_connections.items():
            if exclude_user and key == exclude_user:
                continue
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error en broadcast a {key}: {str(e)}")
    
    async def broadcast_to_users(self, message: Dict, user_ids: List[str]):
        """
        Enviar mensaje a múltiples usuarios específicos.
        
        Args:
            message: Mensaje a enviar
            user_ids: Lista de IDs de usuarios destino
        """
        for user_id in user_ids:
            await self.send_personal(message, user_id)
    
    def update_location(self, user_id: str, lat: float, lng: float):
        """
        Actualizar ubicación de un usuario.
        
        Args:
            user_id: ID del usuario
            lat: Latitud
            lng: Longitud
        """
        self.user_locations[user_id] = {"lat": lat, "lng": lng, "updated_at": datetime.now().isoformat()}
    
    def get_user_location(self, user_id: str) -> Optional[Dict[str, float]]:
        """Obtener ubicación actual de un usuario."""
        return self.user_locations.get(user_id)
    
    def get_nearby_users(self, user_id: str, radius_km: float = 1.0) -> List[str]:
        """
        Encontrar usuarios cercanos.
        
        Args:
            user_id: ID del usuario de referencia
            radius_km: Radio de búsqueda en km
        
        Returns:
            Lista de IDs de usuarios cercanos
        """
        user_location = self.get_user_location(user_id)
        if not user_location:
            return []
        
        nearby = []
        for other_id, location in self.user_locations.items():
            if other_id == user_id:
                continue
            
            distance = calcular_distancia_haversine(
                user_location["lat"], user_location["lng"],
                location["lat"], location["lng"]
            )
            
            if distance <= radius_km:
                nearby.append(other_id)
        
        return nearby


# Instancia global del manager de conexiones
manager = ConnectionManager()


# =====================================================
# MESSAGE HANDLERS
# =====================================================

async def handle_chat_message(websocket: WebSocket, data: Dict, user_id: str, supabase):
    """
    Procesar mensaje de chat.
    
    Args:
        websocket: Conexión WebSocket
        data: Datos del mensaje
        user_id: ID del usuario
        supabase: Cliente de base de datos
    """
    mensaje = data.get("mensaje", "")
    
    if not mensaje:
        await websocket.send_json({
            "type": "error",
            "message": "El mensaje no puede estar vacío"
        })
        return
    
    try:
        # Procesar con el asistente IA
        resultado = asistente.procesar_mensaje(mensaje)
        
        # Guardar en historial si usuario autenticado
        if user_id != "anonymous":
            chat_repo = ChatRepository(supabase)
            
            # Obtener o crear conversación
            conversacion_id = data.get("conversacion_id")
            conv = await chat_repo.get_or_create_conversacion(user_id, conversacion_id)
            
            # Guardar mensaje del usuario
            await chat_repo.add_mensaje(
                conversacion_id=conv['id'],
                rol="user",
                contenido=mensaje,
                intencion=resultado.intencion.value if resultado.intencion else None
            )
            
            # Guardar respuesta del asistente
            msg = await chat_repo.add_mensaje(
                conversacion_id=conv['id'],
                rol="assistant",
                contenido=resultado.texto,
                intencion=resultado.intencion.value if resultado.intencion else None
            )
            
            conversacion_id = conv['id']
            mensaje_id = msg['id']
        else:
            conversacion_id = None
            mensaje_id = None
        
        # Enviar respuesta
        await websocket.send_json({
            "type": "chat",
            "data": {
                "respuesta": resultado.texto,
                "intencion": resultado.intencion.value if resultado.intencion else None,
                "sugerencias": resultado.sugerencias[:3],
                "conversacion_id": conversacion_id,
                "mensaje_id": mensaje_id
            }
        })
        
    except Exception as e:
        logger.error(f"Error en handle_chat_message: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": f"Error procesando mensaje: {str(e)}"
        })


async def handle_location_update(websocket: WebSocket, data: Dict, user_id: str, supabase):
    """
    Procesar actualización de ubicación.
    
    Args:
        websocket: Conexión WebSocket
        data: Datos de ubicación
        user_id: ID del usuario
        supabase: Cliente de base de datos
    """
    lat = data.get("lat")
    lng = data.get("lng")
    
    if lat is None or lng is None:
        await websocket.send_json({
            "type": "error",
            "message": "Se requieren latitud y longitud"
        })
        return
    
    try:
        # Actualizar ubicación en manager
        manager.update_location(user_id, lat, lng)
        
        # Actualizar en base de datos si usuario autenticado
        if user_id != "anonymous":
            from app.repositories.usuario_repo import UsuarioRepository
            usuario_repo = UsuarioRepository(supabase)
            await usuario_repo.update_preferences(
                user_id,
                {"latitud": lat, "longitud": lng}
            )
        
        # Buscar lugares cercanos
        lugar_repo = LugarRepository(supabase)
        lugares_db = await lugar_repo.get_all_active(limit=50)
        
        lugares_cerca = []
        for lugar in lugares_db:
            lugar_lat = lugar.get('lat', lugar.get('latitud', 0))
            lugar_lng = lugar.get('lng', lugar.get('longitud', 0))
            
            distancia = calcular_distancia_haversine(lat, lng, lugar_lat, lugar_lng)
            
            if distancia <= 2.0:  # Radio de 2km
                lugares_cerca.append({
                    "id": lugar.get('id'),
                    "nombre": lugar.get('nombre'),
                    "distancia_km": round(distancia, 2),
                    "icono": lugar.get('icono', '📍')
                })
        
        # Enviar respuesta con lugares cercanos
        await websocket.send_json({
            "type": "location",
            "data": {
                "lat": lat,
                "lng": lng,
                "lugares_cerca": lugares_cerca[:10],
                "total_cerca": len(lugares_cerca)
            }
        })
        
        # Notificar a otros usuarios cercanos (si no es anónimo)
        if user_id != "anonymous":
            nearby_users = manager.get_nearby_users(user_id, radius_km=0.5)
            if nearby_users:
                await manager.broadcast_to_users({
                    "type": "user_nearby",
                    "data": {
                        "user_id": user_id,
                        "location": {"lat": lat, "lng": lng}
                    }
                }, nearby_users)
        
    except Exception as e:
        logger.error(f"Error en handle_location_update: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": f"Error actualizando ubicación: {str(e)}"
        })


async def handle_get_nearby(websocket: WebSocket, data: Dict, user_id: str, supabase):
    """
    Obtener lugares cercanos sin actualizar ubicación.
    
    Args:
        websocket: Conexión WebSocket
        data: Datos de ubicación
        user_id: ID del usuario
        supabase: Cliente de base de datos
    """
    lat = data.get("lat")
    lng = data.get("lng")
    radio_km = data.get("radio_km", 2.0)
    
    if lat is None or lng is None:
        await websocket.send_json({
            "type": "error",
            "message": "Se requieren latitud y longitud"
        })
        return
    
    try:
        lugar_repo = LugarRepository(supabase)
        lugares_db = await lugar_repo.get_all_active(limit=100)
        
        lugares_cerca = []
        for lugar in lugares_db:
            lugar_lat = lugar.get('lat', lugar.get('latitud', 0))
            lugar_lng = lugar.get('lng', lugar.get('longitud', 0))
            
            distancia = calcular_distancia_haversine(lat, lng, lugar_lat, lugar_lng)
            
            if distancia <= radio_km:
                lugares_cerca.append({
                    "id": lugar.get('id'),
                    "nombre": lugar.get('nombre'),
                    "descripcion_corta": lugar.get('descripcion_corta', lugar.get('descripcion', '')[:100]),
                    "lat": lugar_lat,
                    "lng": lugar_lng,
                    "distancia_km": round(distancia, 2),
                    "icono": lugar.get('icono', '📍'),
                    "rating": lugar.get('rating', 0)
                })
        
        # Ordenar por distancia
        lugares_cerca.sort(key=lambda x: x["distancia_km"])
        
        await websocket.send_json({
            "type": "nearby",
            "data": {
                "lugares": lugares_cerca[:20],
                "total": len(lugares_cerca),
                "center": {"lat": lat, "lng": lng},
                "radio_km": radio_km
            }
        })
        
    except Exception as e:
        logger.error(f"Error en handle_get_nearby: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": f"Error obteniendo lugares cercanos: {str(e)}"
        })


async def handle_ping(websocket: WebSocket):
    """Responder a ping con pong."""
    await websocket.send_json({
        "type": "pong",
        "timestamp": datetime.now().isoformat()
    })


# =====================================================
# WEBSOCKET ENDPOINT
# =====================================================

@router.websocket("/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    token: Optional[str] = Query(None),
    supabase = Depends(get_db)
):
    """
    Endpoint WebSocket principal.
    
    Tipos de mensajes soportados:
    
    1. Chat:
        {
            "type": "chat",
            "data": {
                "mensaje": "¿Dónde puedo bailar salsa?",
                "conversacion_id": 123 (opcional)
            }
        }
    
    2. Ubicación:
        {
            "type": "location",
            "data": {
                "lat": 3.4516,
                "lng": -76.5320
            }
        }
    
    3. Obtener cercanos:
        {
            "type": "get_nearby",
            "data": {
                "lat": 3.4516,
                "lng": -76.5320,
                "radio_km": 2.0
            }
        }
    
    4. Ping:
        {
            "type": "ping"
        }
    """
    # Intentar obtener usuario autenticado por token
    user_id = client_id
    is_authenticated = False
    
    if token:
        try:
            # Verificar token con Supabase
            user_response = supabase.auth.get_user(token)
            if user_response and user_response.user:
                user_id = user_response.user.id
                is_authenticated = True
                logger.info(f"Usuario autenticado vía WebSocket: {user_id}")
        except Exception as e:
            logger.warning(f"Token inválido en WebSocket: {str(e)}")
    
    # Registrar conexión
    await manager.connect(websocket, user_id if is_authenticated else None)
    
    try:
        # Enviar mensaje de bienvenida
        await websocket.send_json({
            "type": "welcome",
            "data": {
                "client_id": client_id,
                "user_id": user_id if is_authenticated else None,
                "authenticated": is_authenticated,
                "message": "Conectado a LoCALIzate WebSocket"
            }
        })
        
        # Escuchar mensajes
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                msg_type = message.get("type")
                msg_data = message.get("data", {})
                
                logger.debug(f"Mensaje recibido: {msg_type} de {user_id}")
                
                if msg_type == "chat":
                    await handle_chat_message(websocket, msg_data, user_id, supabase)
                
                elif msg_type == "location":
                    await handle_location_update(websocket, msg_data, user_id, supabase)
                
                elif msg_type == "get_nearby":
                    await handle_get_nearby(websocket, msg_data, user_id, supabase)
                
                elif msg_type == "ping":
                    await handle_ping(websocket)
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Tipo de mensaje desconocido: {msg_type}"
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Formato JSON inválido"
                })
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error procesando mensaje: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error interno: {str(e)}"
                })
                
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, user_id if is_authenticated else None)
        logger.info(f"WebSocket desconectado: {user_id}")


# =====================================================
# INFO ENDPOINT
# =====================================================

@router.get("/info")
async def get_websocket_info():
    """Obtener información sobre el servicio WebSocket."""
    return {
        "servicio": "WebSocket - LoCALIzate",
        "version": "1.0.0",
        "descripcion": "Conexiones WebSocket para funcionalidades en tiempo real",
        "tipos_mensaje": {
            "chat": "Enviar mensaje al asistente virtual",
            "location": "Actualizar ubicación del usuario",
            "get_nearby": "Obtener lugares cercanos",
            "ping": "Mantener conexión activa"
        },
        "conexiones_activas": manager._count_connections(),
        "estado": "operativo"
    }