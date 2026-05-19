"""
Ruta Repository for LoCALIzate Backend
=====================================

Repository for user routes and itineraries.
Provides specialized queries for routes including:
    - Route creation with optimization
    - Route details management
    - Route duplication and sharing
    - Route statistics (most popular, recent)
    - Route templates for recommendations

Inherits from BaseRepository for common CRUD operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from math import radians, sin, cos, sqrt, atan2
import logging

from supabase import Client
from app.repositories.base_repo import BaseRepository
from app.core.exceptions import DatabaseException, NotFoundException

# Configure logging
logger = logging.getLogger(__name__)


class RutaRepository(BaseRepository):
    """
    Repository for user routes.
    
    Attributes:
        supabase: Supabase client instance
        table_name: "rutas_usuario" (table name in Supabase)
    """
    
    def __init__(self, supabase: Client):
        """Initialize repository with 'rutas_usuario' table."""
        super().__init__(supabase, "rutas_usuario")
        self.detalle_table = supabase.table("ruta_detalle")
    
    # =====================================================
    # HELPER FUNCTIONS
    # =====================================================
    
    @staticmethod
    def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance in kilometers between two points."""
        R = 6371
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lng = radians(lng2 - lng1)
        
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def _calcular_tiempo_estimado(distancia_km: float, velocidad_kmh: float = 30.0) -> int:
        """Calculate estimated time in minutes."""
        return int((distancia_km / velocidad_kmh) * 60)
    
    async def _calcular_distancias_ruta(
        self,
        lugar_ids: List[int],
        inicio_lat: Optional[float] = None,
        inicio_lng: Optional[float] = None
    ) -> tuple:
        """
        Calculate distances and times between places in a route.
        
        Args:
            lugar_ids: List of place IDs in order
            inicio_lat: Starting latitude (optional)
            inicio_lng: Starting longitude (optional)
        
        Returns:
            Tuple of (distancia_total_km, tiempo_total_min, detalles)
        """
        # Get place coordinates
        places = []
        for lugar_id in lugar_ids:
            result = self.supabase.table("lugares")\
                .select("id, nombre, latitud, longitud")\
                .eq("id", lugar_id)\
                .single()\
                .execute()
            if result.data:
                places.append(result.data)
        
        if not places:
            return 0, 0, []
        
        distancia_total = 0
        tiempo_total = 0
        detalles = []
        
        prev_lat = inicio_lat
        prev_lng = inicio_lng
        
        for i, place in enumerate(places):
            if prev_lat is not None and prev_lng is not None:
                dist = self._haversine_distance(prev_lat, prev_lng, place["latitud"], place["longitud"])
                tiempo = self._calcular_tiempo_estimado(dist)
                distancia_total += dist
                tiempo_total += tiempo
                
                detalles.append({
                    "orden": i + 1,
                    "lugar_id": place["id"],
                    "lugar_nombre": place["nombre"],
                    "lugar_latitud": place["latitud"],
                    "lugar_longitud": place["longitud"],
                    "distancia_desde_anterior_km": round(dist, 2),
                    "tiempo_estimado_min": tiempo
                })
            else:
                detalles.append({
                    "orden": i + 1,
                    "lugar_id": place["id"],
                    "lugar_nombre": place["nombre"],
                    "lugar_latitud": place["latitud"],
                    "lugar_longitud": place["longitud"],
                    "distancia_desde_anterior_km": 0,
                    "tiempo_estimado_min": 0
                })
            
            prev_lat = place["latitud"]
            prev_lng = place["longitud"]
        
        return round(distancia_total, 2), tiempo_total, detalles
    
    # =====================================================
    # ROUTE CRUD OPERATIONS
    # =====================================================
    
    async def create_route(
        self,
        usuario_id: str,
        nombre: str,
        lugar_ids: List[int],
        descripcion: Optional[str] = None,
        fecha_visita: Optional[date] = None,
        hora_inicio: Optional[str] = None,
        inicio_lat: Optional[float] = None,
        inicio_lng: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create a new route with calculated distances.
        
        Args:
            usuario_id: User ID
            nombre: Route name
            lugar_ids: List of place IDs in order
            descripcion: Route description
            fecha_visita: Visit date
            hora_inicio: Start time
            inicio_lat: Starting latitude
            inicio_lng: Starting longitude
        
        Returns:
            Created route with details
        """
        try:
            # Calculate distances
            distancia_total, tiempo_total, detalles = await self._calcular_distancias_ruta(
                lugar_ids, inicio_lat, inicio_lng
            )
            
            # Create route
            route_data = {
                "usuario_id": usuario_id,
                "nombre": nombre,
                "descripcion": descripcion,
                "fecha_visita": fecha_visita.isoformat() if fecha_visita else None,
                "hora_inicio": hora_inicio,
                "distancia_total_km": distancia_total,
                "tiempo_estimado_min": tiempo_total,
                "completada": False,
                "compartida": False,
                "activa": True,
                "created_at": datetime.now().isoformat()
            }
            
            # Insert route
            result = self._table.insert(route_data).execute()
            
            if not result.data or len(result.data) == 0:
                raise DatabaseException(
                    detail="No se pudo crear la ruta",
                    operation="create_route",
                    table=self.table_name
                )
            
            route = result.data[0]
            route_id = route["id"]
            
            # Create route details
            for detalle in detalles:
                detalle["ruta_id"] = route_id
                detalle["created_at"] = datetime.now().isoformat()
            
            if detalles:
                self.detalle_table.insert(detalles).execute()
            
            # Get complete route with details
            return await self.get_route_with_details(route_id)
            
        except Exception as e:
            self._handle_error(e, "create_route", usuario_id=usuario_id, nombre=nombre)
            raise
    
    async def get_route_with_details(
        self,
        ruta_id: int
    ) -> Dict[str, Any]:
        """
        Get route with all details.
        
        Args:
            ruta_id: Route ID
        
        Returns:
            Route with details
        """
        try:
            # Get route
            route = await self.get_by_id_or_fail(ruta_id)
            
            # Get details
            details = self.detalle_table\
                .select("*")\
                .eq("ruta_id", ruta_id)\
                .order("orden")\
                .execute()
            
            route["detalles"] = details.data if details.data else []
            route["cantidad_lugares"] = len(route["detalles"])
            
            return route
            
        except NotFoundException:
            raise
        except Exception as e:
            self._handle_error(e, "get_route_with_details", ruta_id=ruta_id)
            raise
    
    async def get_user_routes(
        self,
        usuario_id: str,
        limit: int = 20,
        offset: int = 0,
        only_active: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all routes for a user.
        
        Args:
            usuario_id: User ID
            limit: Maximum number of records
            offset: Number of records to skip
            only_active: If True, only active routes
        
        Returns:
            List of user routes with basic info
        """
        filters = {"usuario_id": usuario_id}
        if only_active:
            filters["activa"] = True
        
        routes = await self.get_all(
            filters=filters,
            limit=limit,
            offset=offset,
            order_by="created_at",
            order_desc=True
        )
        
        # Add place count to each route
        for route in routes:
            details = self.detalle_table\
                .select("id", count="exact")\
                .eq("ruta_id", route["id"])\
                .execute()
            route["cantidad_lugares"] = getattr(details, 'count', 0) or len(details.data or [])
        
        return routes
    
    async def update_route(
        self,
        ruta_id: int,
        usuario_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a route.
        
        Args:
            ruta_id: Route ID
            usuario_id: User ID (for ownership check)
            data: Update data
        
        Returns:
            Updated route
        """
        # Verify ownership
        route = await self.get_by_id(ruta_id)
        if not route:
            raise NotFoundException(resource_type="Ruta", resource_id=ruta_id)
        
        if route["usuario_id"] != usuario_id:
            raise DatabaseException(
                detail="No tienes permiso para modificar esta ruta",
                operation="update_route",
                table=self.table_name
            )
        
        return await self.update(ruta_id, data)
    
    async def delete_route(
        self,
        ruta_id: int,
        usuario_id: str,
        soft_delete: bool = True
    ) -> bool:
        """
        Delete a route.
        
        Args:
            ruta_id: Route ID
            usuario_id: User ID (for ownership check)
            soft_delete: If True, sets activa=False instead of hard delete
        
        Returns:
            True if deleted
        """
        # Verify ownership
        route = await self.get_by_id(ruta_id)
        if not route:
            return False
        
        if route["usuario_id"] != usuario_id:
            return False
        
        return await self.delete(ruta_id, soft_delete=soft_delete)
    
    # =====================================================
    # ROUTE DUPLICATION AND SHARING
    # =====================================================
    
    async def duplicate_route(
        self,
        ruta_id: int,
        nuevo_usuario_id: str,
        nuevo_nombre: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Duplicate an existing route for a user.
        
        Args:
            ruta_id: Original route ID
            nuevo_usuario_id: New user ID
            nuevo_nombre: New route name (optional)
        
        Returns:
            New route
        """
        try:
            # Get original route
            original = await self.get_route_with_details(ruta_id)
            
            # Create new route name
            if not nuevo_nombre:
                nuevo_nombre = f"Copia de {original['nombre']}"
            
            # Extract place IDs in order
            lugar_ids = [d["lugar_id"] for d in original.get("detalles", [])]
            
            # Create new route
            return await self.create_route(
                usuario_id=nuevo_usuario_id,
                nombre=nuevo_nombre,
                lugar_ids=lugar_ids,
                descripcion=original.get("descripcion"),
                fecha_visita=None,  # Don't copy date
                hora_inicio=original.get("hora_inicio")
            )
            
        except Exception as e:
            self._handle_error(e, "duplicate_route", ruta_id=ruta_id, nuevo_usuario_id=nuevo_usuario_id)
            raise
    
    async def share_route(
        self,
        ruta_id: int,
        usuario_id: str
    ) -> Dict[str, Any]:
        """
        Share a route (set compartida=True).
        
        Args:
            ruta_id: Route ID
            usuario_id: User ID (for ownership check)
        
        Returns:
            Updated route
        """
        return await self.update_route(ruta_id, usuario_id, {"compartida": True})
    
    async def get_shared_routes(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get public shared routes.
        
        Args:
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of shared routes
        """
        return await self.get_all(
            filters={"compartida": True, "activa": True},
            limit=limit,
            offset=offset,
            order_by="created_at",
            order_desc=True
        )
    
    # =====================================================
    # ROUTE OPTIMIZATION
    # =====================================================
    
    async def optimize_route(
        self,
        lugar_ids: List[int],
        inicio_lat: float,
        inicio_lng: float
    ) -> List[int]:
        """
        Optimize route order using nearest neighbor algorithm.
        
        Args:
            lugar_ids: List of place IDs to visit
            inicio_lat: Starting latitude
            inicio_lng: Starting longitude
        
        Returns:
            Optimized list of place IDs
        """
        if len(lugar_ids) <= 1:
            return lugar_ids
        
        # Get coordinates for all places
        places = []
        for lugar_id in lugar_ids:
            result = self.supabase.table("lugares")\
                .select("id, latitud, longitud")\
                .eq("id", lugar_id)\
                .single()\
                .execute()
            if result.data:
                places.append(result.data)
        
        if not places:
            return lugar_ids
        
        # Nearest neighbor algorithm
        unvisited = places.copy()
        optimized = []
        current_lat = inicio_lat
        current_lng = inicio_lng
        
        while unvisited:
            # Find nearest unvisited place
            nearest_idx = 0
            nearest_dist = float('inf')
            
            for i, place in enumerate(unvisited):
                dist = self._haversine_distance(
                    current_lat, current_lng,
                    place["latitud"], place["longitud"]
                )
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_idx = i
            
            nearest = unvisited.pop(nearest_idx)
            optimized.append(nearest["id"])
            current_lat = nearest["latitud"]
            current_lng = nearest["longitud"]
        
        return optimized
    
    # =====================================================
    # ROUTE STATISTICS
    # =====================================================
    
    async def get_route_stats(self) -> Dict[str, Any]:
        """
        Get global route statistics.
        
        Returns:
            Dictionary with route statistics
        """
        try:
            # Total routes
            total = await self.get_count(filters={"activa": True})
            
            # Shared routes
            shared = await self.get_count(filters={"compartida": True, "activa": True})
            
            # Completed routes
            completed = await self.get_count(filters={"completada": True, "activa": True})
            
            # Average places per route
            result = self.detalle_table.select("ruta_id", count="exact").execute()
            
            return {
                "total_rutas": total,
                "rutas_compartidas": shared,
                "rutas_completadas": completed,
                "tasa_completacion": round((completed / total * 100), 1) if total > 0 else 0
            }
            
        except Exception as e:
            self._handle_error(e, "get_route_stats")
            return {}
    
    async def get_most_popular_routes(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get most popular routes (most duplicated/shared).
        
        Args:
            limit: Maximum number of records
        
        Returns:
            List of popular routes
        """
        try:
            # This is a simplified version
            # In production, track copy count
            result = self._table.select("*")\
                .eq("compartida", True)\
                .eq("activa", True)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            routes = result.data if result.data else []
            
            # Add place count to each
            for route in routes:
                details_count = self.detalle_table\
                    .select("id", count="exact")\
                    .eq("ruta_id", route["id"])\
                    .execute()
                route["cantidad_lugares"] = getattr(details_count, 'count', 0) or 0
            
            return routes
            
        except Exception as e:
            self._handle_error(e, "get_most_popular_routes")
            return []
    
    async def mark_route_completed(
        self,
        ruta_id: int,
        usuario_id: str
    ) -> Dict[str, Any]:
        """
        Mark a route as completed.
        
        Args:
            ruta_id: Route ID
            usuario_id: User ID
        
        Returns:
            Updated route
        """
        return await self.update_route(ruta_id, usuario_id, {"completada": True})
    
    async def get_route_templates(self) -> List[Dict[str, Any]]:
        """
        Get predefined route templates.
        
        Returns:
            List of route templates
        """
        # Predefined route templates for Cali
        templates = [
            {
                "id": 1,
                "nombre": "Tour Cultural por el Centro",
                "descripcion": "Recorrido por los principales sitios culturales del centro de Cali",
                "duracion_horas": 4,
                "dificultad": "fácil",
                "categoria": "cultura",
                "icono": "🎭",
                "lugares_sugeridos": [3, 2, 7, 1]  # La Ermita, Gato, San Antonio, Cristo Rey
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
                "descripcion": "Los mejores sabores de la cocina del Pacífico",
                "duracion_horas": 4,
                "dificultad": "fácil",
                "categoria": "gastronomia",
                "icono": "🍽️",
                "lugares_sugeridos": [11, 15, 16]  # Bulevar, Morada Ancestral, Palomulata
            },
            {
                "id": 5,
                "nombre": "Aventura Extrema",
                "descripcion": "Para los amantes de la adrenalina",
                "duracion_horas": 8,
                "dificultad": "difícil",
                "categoria": "aventura",
                "icono": "🧗",
                "lugares_sugeridos": [17, 18, 10]  # Parapente, Chorrera, Farallones
            }
        ]
        
        return templates


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("RutaRepository module loaded successfully")
    print("\nAvailable custom methods:")
    methods = [
        "create_route()",
        "get_route_with_details()",
        "get_user_routes()",
        "update_route()",
        "delete_route()",
        "duplicate_route()",
        "share_route()",
        "get_shared_routes()",
        "optimize_route()",
        "get_route_stats()",
        "get_most_popular_routes()",
        "mark_route_completed()",
        "get_route_templates()"
    ]
    for method in methods:
        print(f"  - {method}")