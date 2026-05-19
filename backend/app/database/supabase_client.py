"""
Cliente Supabase para LoCALIzate / LoCALIzate Backend
====================================================

Maneja la conexión y operaciones con Supabase.
Implementa patrón Singleton para una sola instancia del cliente.

Características:
    - Singleton pattern para cliente único
    - Métodos CRUD para entidades principales
    - Manejo de errores y logging
    - Soporte para filtros y paginación

Usage:
    from database import supabase_client
    
    # Obtener cliente
    client = supabase_client.get_client()
    
    # Operaciones
    lugares = supabase_client.get_lugares()
    eventos = supabase_client.get_eventos(destacados_only=True)
"""

import os
import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Cliente Singleton para Supabase.
    Maneja conexión y operaciones de base de datos.
    """
    
    _instance = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        """Implementación del patrón Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar el cliente Supabase si no existe."""
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Inicializar la conexión con Supabase."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados en .env")
        
        try:
            self._client = create_client(supabase_url, supabase_key)
            logger.info("✅ Cliente Supabase inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando cliente Supabase: {str(e)}")
            raise
    
    def get_client(self) -> Client:
        """
        Obtener el cliente Supabase.
        
        Returns:
            Client: Cliente de Supabase
        """
        if self._client is None:
            self._initialize_client()
        return self._client
    
    # =====================================================
    # OPERACIONES PARA LUGARES
    # =====================================================
    
    def get_lugares(self, filtro: Optional[Dict] = None, limit: int = 100, offset: int = 0) -> Any:
        """
        Obtener lugares turísticos con filtros opcionales.
        
        Args:
            filtro: Diccionario con filtros (ej: {"interes": "cultura"})
            limit: Límite de resultados
            offset: Desplazamiento para paginación
        
        Returns:
            Resultado de la consulta
        """
        try:
            query = self._client.table("lugares").select("*")
            
            if filtro and filtro.get("interes"):
                query = query.eq("interes", filtro["interes"])
            
            if filtro and filtro.get("destacado"):
                query = query.eq("destacado", True)
            
            query = query.range(offset, offset + limit - 1)
            result = query.execute()
            
            logger.debug(f"Obtenidos {len(result.data)} lugares")
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo lugares: {str(e)}")
            raise
    
    def get_lugar_by_id(self, lugar_id: int) -> Optional[Dict]:
        """
        Obtener un lugar por su ID.
        
        Args:
            lugar_id: ID del lugar
        
        Returns:
            Diccionario con datos del lugar o None
        """
        try:
            result = self._client.table("lugares").select("*").eq("id", lugar_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo lugar {lugar_id}: {str(e)}")
            return None
    
    # =====================================================
    # OPERACIONES PARA EVENTOS
    # =====================================================
    
    def get_eventos(self, destacados_only: bool = False, limit: int = 50) -> Any:
        """
        Obtener eventos.
        
        Args:
            destacados_only: Si es True, solo eventos destacados
            limit: Límite de resultados
        
        Returns:
            Resultado de la consulta
        """
        try:
            query = self._client.table("eventos").select("*")
            
            if destacados_only:
                query = query.eq("destacado", True)
            
            query = query.limit(limit)
            result = query.execute()
            
            logger.debug(f"Obtenidos {len(result.data)} eventos")
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo eventos: {str(e)}")
            raise
    
    def get_evento_by_id(self, evento_id: int) -> Optional[Dict]:
        """
        Obtener un evento por su ID.
        
        Args:
            evento_id: ID del evento
        
        Returns:
            Diccionario con datos del evento o None
        """
        try:
            result = self._client.table("eventos").select("*").eq("id", evento_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo evento {evento_id}: {str(e)}")
            return None
    
    def get_eventos_proximos(self, dias: int = 30) -> List[Dict]:
        """
        Obtener eventos próximos.
        
        Args:
            dias: Número de días hacia adelante
        
        Returns:
            Lista de eventos próximos
        """
        try:
            from datetime import datetime, timedelta
            
            hoy = datetime.now().date()
            fecha_limite = hoy + timedelta(days=dias)
            
            result = self._client.table("eventos").select("*").execute()
            
            proximos = []
            for evento in result.data:
                fecha_inicio = datetime.strptime(evento['fecha_inicio'], '%Y-%m-%d').date()
                if hoy <= fecha_inicio <= fecha_limite:
                    proximos.append(evento)
            
            return sorted(proximos, key=lambda x: x['fecha_inicio'])
            
        except Exception as e:
            logger.error(f"Error obteniendo eventos próximos: {str(e)}")
            return []
    
    # =====================================================
    # OPERACIONES PARA RUTAS
    # =====================================================
    
    def get_rutas_usuario(self, usuario_id: int) -> Any:
        """
        Obtener rutas guardadas de un usuario.
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            Resultado de la consulta
        """
        try:
            result = self._client.table("rutas_usuario").select("*").eq("usuario_id", usuario_id).execute()
            return result
        except Exception as e:
            logger.error(f"Error obteniendo rutas del usuario {usuario_id}: {str(e)}")
            raise
    
    def guardar_ruta(self, usuario_id: int, lugares_ids: List[int], orden_optimizado: List[int]) -> Any:
        """
        Guardar una ruta optimizada para un usuario.
        
        Args:
            usuario_id: ID del usuario
            lugares_ids: Lista de IDs de lugares
            orden_optimizado: Orden optimizado de visita
        
        Returns:
            Resultado de la inserción
        """
        try:
            from datetime import datetime
            
            data = {
                "usuario_id": usuario_id,
                "lugares_ids": lugares_ids,
                "orden_optimizado": orden_optimizado,
                "fecha_creacion": datetime.now().isoformat()
            }
            
            result = self._client.table("rutas_usuario").insert(data).execute()
            logger.info(f"Ruta guardada para usuario {usuario_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error guardando ruta: {str(e)}")
            raise
    
    # =====================================================
    # OPERACIONES PARA USUARIOS
    # =====================================================
    
    def guardar_preferencias_usuario(self, usuario_id: int, intereses: List[str]) -> Any:
        """
        Guardar preferencias de usuario.
        
        Args:
            usuario_id: ID del usuario
            intereses: Lista de intereses del usuario
        
        Returns:
            Resultado de la actualización
        """
        try:
            result = self._client.table("usuarios").update({
                "intereses": intereses
            }).eq("id", usuario_id).execute()
            
            logger.info(f"Preferencias actualizadas para usuario {usuario_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error guardando preferencias: {str(e)}")
            raise
    
    def get_usuario_by_id(self, usuario_id: int) -> Optional[Dict]:
        """
        Obtener un usuario por su ID.
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            Diccionario con datos del usuario o None
        """
        try:
            result = self._client.table("usuarios").select("*").eq("id", usuario_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario {usuario_id}: {str(e)}")
            return None
    
    # =====================================================
    # OPERACIONES PARA CATEGORÍAS
    # =====================================================
    
    def get_categorias(self, activas_only: bool = True) -> List[Dict]:
        """
        Obtener categorías de interés.
        
        Args:
            activas_only: Si es True, solo categorías activas
        
        Returns:
            Lista de categorías
        """
        try:
            query = self._client.table("categorias").select("*")
            
            if activas_only:
                query = query.eq("activo", True)
            
            result = query.order("orden").execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error obteniendo categorías: {str(e)}")
            return []
    
    # =====================================================
    # OPERACIONES DE FAVORITOS
    # =====================================================
    
    def add_favorito(self, usuario_id: int, lugar_id: int) -> bool:
        """
        Agregar lugar a favoritos.
        
        Args:
            usuario_id: ID del usuario
            lugar_id: ID del lugar
        
        Returns:
            True si se agregó correctamente
        """
        try:
            from datetime import datetime
            
            data = {
                "usuario_id": usuario_id,
                "lugar_id": lugar_id,
                "fecha_agregado": datetime.now().isoformat()
            }
            
            self._client.table("favoritos").insert(data).execute()
            logger.info(f"Lugar {lugar_id} agregado a favoritos de usuario {usuario_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error agregando favorito: {str(e)}")
            return False
    
    def remove_favorito(self, usuario_id: int, lugar_id: int) -> bool:
        """
        Eliminar lugar de favoritos.
        
        Args:
            usuario_id: ID del usuario
            lugar_id: ID del lugar
        
        Returns:
            True si se eliminó correctamente
        """
        try:
            self._client.table("favoritos").delete().eq("usuario_id", usuario_id).eq("lugar_id", lugar_id).execute()
            logger.info(f"Lugar {lugar_id} eliminado de favoritos de usuario {usuario_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando favorito: {str(e)}")
            return False
    
    def get_favoritos_usuario(self, usuario_id: int) -> List[Dict]:
        """
        Obtener favoritos de un usuario.
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            Lista de lugares favoritos
        """
        try:
            result = self._client.table("favoritos").select("*, lugares(*)").eq("usuario_id", usuario_id).execute()
            
            favoritos = []
            for item in result.data or []:
                if item.get("lugares"):
                    lugar = item["lugares"]
                    lugar["fecha_agregado"] = item.get("fecha_agregado")
                    favoritos.append(lugar)
            
            return favoritos
            
        except Exception as e:
            logger.error(f"Error obteniendo favoritos: {str(e)}")
            return []
    
    # =====================================================
    # OPERACIONES DE RESEÑAS
    # =====================================================
    
    def add_resena(self, usuario_id: int, lugar_id: int, rating: int, comentario: str = "") -> bool:
        """
        Agregar reseña a un lugar.
        
        Args:
            usuario_id: ID del usuario
            lugar_id: ID del lugar
            rating: Calificación (1-5)
            comentario: Comentario opcional
        
        Returns:
            True si se agregó correctamente
        """
        try:
            from datetime import datetime
            
            data = {
                "usuario_id": usuario_id,
                "lugar_id": lugar_id,
                "rating": rating,
                "comentario": comentario,
                "fecha": datetime.now().isoformat()
            }
            
            self._client.table("resenas").insert(data).execute()
            logger.info(f"Reseña agregada para lugar {lugar_id} por usuario {usuario_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error agregando reseña: {str(e)}")
            return False
    
    # =====================================================
    # UTILIDADES
    # =====================================================
    
    def test_connection(self) -> bool:
        """
        Probar conexión con Supabase.
        
        Returns:
            True si la conexión es exitosa
        """
        try:
            result = self._client.table("categorias").select("count", count="exact").limit(1).execute()
            logger.info("✅ Conexión a Supabase exitosa")
            return True
        except Exception as e:
            logger.error(f"❌ Error de conexión: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """
        Obtener estadísticas de la base de datos.
        
        Returns:
            Diccionario con conteos de entidades
        """
        stats = {}
        
        try:
            lugares = self._client.table("lugares").select("id", count="exact").execute()
            stats["total_lugares"] = getattr(lugares, 'count', 0) or 0
        except:
            stats["total_lugares"] = 0
        
        try:
            eventos = self._client.table("eventos").select("id", count="exact").execute()
            stats["total_eventos"] = getattr(eventos, 'count', 0) or 0
        except:
            stats["total_eventos"] = 0
        
        try:
            usuarios = self._client.table("usuarios").select("id", count="exact").execute()
            stats["total_usuarios"] = getattr(usuarios, 'count', 0) or 0
        except:
            stats["total_usuarios"] = 0
        
        return stats


# =====================================================
# INSTANCIA GLOBAL
# =====================================================

# Instancia única del cliente
supabase_client = SupabaseClient()


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Supabase Client - LoCALIzate")
    print("=" * 50)
    
    # Probar conexión
    print("\n🔌 Probando conexión...")
    if supabase_client.test_connection():
        print("✅ Conexión exitosa")
        
        # Obtener estadísticas
        stats = supabase_client.get_stats()
        print(f"\n📊 Estadísticas:")
        print(f"   Total lugares: {stats.get('total_lugares', 0)}")
        print(f"   Total eventos: {stats.get('total_eventos', 0)}")
        print(f"   Total usuarios: {stats.get('total_usuarios', 0)}")
        
        # Probar obtener lugares
        lugares = supabase_client.get_lugares(limit=5)
        print(f"\n📍 Primeros lugares:")
        for lugar in lugares.data[:3]:
            print(f"   - {lugar.get('nombre')} ({lugar.get('interes')})")
    
    print("\n✅ Supabase client ready")