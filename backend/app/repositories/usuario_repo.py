"""
Usuario Repository for LoCALIzate Backend
========================================

Repository for user profiles and preferences.
Provides specialized queries for users including:
    - User profile management
    - Interest management
    - Favorite places management
    - User statistics (routes, favorites, reviews)
    - User preferences (language, theme, notifications)

Inherits from BaseRepository for common CRUD operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from supabase import Client
from app.repositories.base_repo import BaseRepository
from app.core.exceptions import DatabaseException, NotFoundException

# Configure logging
logger = logging.getLogger(__name__)


class UsuarioRepository(BaseRepository):
    """
    Repository for user profiles.
    
    Attributes:
        supabase: Supabase client instance
        table_name: "perfiles" (table name in Supabase)
    """
    
    def __init__(self, supabase: Client):
        """Initialize repository with 'perfiles' table."""
        super().__init__(supabase, "perfiles")
    
    # =====================================================
    # USER PROFILE QUERIES
    # =====================================================
    
    async def get_by_email(
        self,
        email: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get user by email address.
        
        Args:
            email: User email address
        
        Returns:
            User data or None if not found
        """
        try:
            result = self._table.select("*").eq("email", email).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            self._handle_error(e, "get_by_email", email=email)
            return None
    
    async def get_or_create_by_auth_id(
        self,
        auth_id: str,
        email: str,
        nombre: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get user by auth_id or create if not exists.
        
        Args:
            auth_id: Supabase Auth user ID
            email: User email
            nombre: User name (optional)
        
        Returns:
            User profile
        """
        try:
            # Try to get existing user
            result = self._table.select("*").eq("id", auth_id).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            # Create new user profile
            user_data = {
                "id": auth_id,
                "email": email,
                "nombre": nombre or email.split("@")[0],
                "created_at": datetime.now().isoformat()
            }
            
            create_result = self._table.insert(user_data).execute()
            
            if create_result.data and len(create_result.data) > 0:
                logger.info(f"Created new user profile for {email}")
                return create_result.data[0]
            
            raise DatabaseException(
                detail="No se pudo crear el perfil de usuario",
                operation="get_or_create_by_auth_id",
                table=self.table_name
            )
            
        except Exception as e:
            self._handle_error(e, "get_or_create_by_auth_id", auth_id=auth_id, email=email)
            raise
    
    async def update_last_login(
        self,
        usuario_id: str
    ) -> None:
        """
        Update user's last login timestamp.
        
        Args:
            usuario_id: User ID
        """
        try:
            await self.update(
                usuario_id,
                {"last_login": datetime.now().isoformat()},
                id_column="id"
            )
        except Exception as e:
            logger.warning(f"Failed to update last_login for {usuario_id}: {str(e)}")
    
    async def get_profile_with_stats(
        self,
        usuario_id: str
    ) -> Dict[str, Any]:
        """
        Get user profile with statistics.
        
        Args:
            usuario_id: User ID
        
        Returns:
            User profile with stats (rutas_count, favoritos_count, resenas_count)
        """
        try:
            # Get user profile
            user = await self.get_by_id_or_fail(usuario_id, id_column="id")
            
            # Get routes count
            rutas_result = self.supabase.table("rutas_usuario")\
                .select("id", count="exact")\
                .eq("usuario_id", usuario_id)\
                .execute()
            rutas_count = getattr(rutas_result, 'count', 0) or len(rutas_result.data or [])
            
            # Get favorites count
            favoritos_result = self.supabase.table("favoritos")\
                .select("id", count="exact")\
                .eq("usuario_id", usuario_id)\
                .execute()
            favoritos_count = getattr(favoritos_result, 'count', 0) or len(favoritos_result.data or [])
            
            # Get reviews count
            resenas_result = self.supabase.table("resenas")\
                .select("id", count="exact")\
                .eq("usuario_id", usuario_id)\
                .execute()
            resenas_count = getattr(resenas_result, 'count', 0) or len(resenas_result.data or [])
            
            # Add stats to user data
            user["total_rutas"] = rutas_count
            user["total_favoritos"] = favoritos_count
            user["total_resenas"] = resenas_count
            
            return user
            
        except NotFoundException:
            raise
        except Exception as e:
            self._handle_error(e, "get_profile_with_stats", usuario_id=usuario_id)
            raise
    
    # =====================================================
    # USER INTERESTS QUERIES
    # =====================================================
    
    async def get_intereses(
        self,
        usuario_id: str
    ) -> List[str]:
        """
        Get user's interests.
        
        Args:
            usuario_id: User ID
        
        Returns:
            List of interest categories
        """
        try:
            result = self.supabase.table("usuario_intereses")\
                .select("interes")\
                .eq("usuario_id", usuario_id)\
                .execute()
            
            if result.data:
                return [item["interes"] for item in result.data]
            return []
            
        except Exception as e:
            self._handle_error(e, "get_intereses", usuario_id=usuario_id)
            return []
    
    async def set_intereses(
        self,
        usuario_id: str,
        intereses: List[str]
    ) -> List[str]:
        """
        Set user's interests (replaces all existing).
        
        Args:
            usuario_id: User ID
            intereses: List of interest categories
        
        Returns:
            Updated list of interests
        """
        valid_intereses = ["cultura", "naturaleza", "gastronomia", "salsa", "aventura"]
        
        # Validate interests
        for interes in intereses:
            if interes not in valid_intereses:
                raise ValueError(f"Interés inválido: {interes}. Debe ser uno de: {valid_intereses}")
        
        try:
            # Delete existing interests
            self.supabase.table("usuario_intereses")\
                .delete()\
                .eq("usuario_id", usuario_id)\
                .execute()
            
            # Insert new interests
            if intereses:
                data = [{"usuario_id": usuario_id, "interes": i} for i in intereses]
                self.supabase.table("usuario_intereses").insert(data).execute()
            
            # Update user profile intereses field (for quick access)
            await self.update(
                usuario_id,
                {"intereses": intereses},
                id_column="id"
            )
            
            logger.info(f"Updated interests for user {usuario_id}: {intereses}")
            return intereses
            
        except Exception as e:
            self._handle_error(e, "set_intereses", usuario_id=usuario_id, intereses=intereses)
            return []
    
    async def add_interes(
        self,
        usuario_id: str,
        interes: str
    ) -> List[str]:
        """
        Add a single interest to user.
        
        Args:
            usuario_id: User ID
            interes: Interest category to add
        
        Returns:
            Updated list of interests
        """
        current = await self.get_intereses(usuario_id)
        
        if interes not in current:
            current.append(interes)
            return await self.set_intereses(usuario_id, current)
        
        return current
    
    async def remove_interes(
        self,
        usuario_id: str,
        interes: str
    ) -> List[str]:
        """
        Remove a single interest from user.
        
        Args:
            usuario_id: User ID
            interes: Interest category to remove
        
        Returns:
            Updated list of interests
        """
        current = await self.get_intereses(usuario_id)
        
        if interes in current:
            current.remove(interes)
            return await self.set_intereses(usuario_id, current)
        
        return current
    
    # =====================================================
    # FAVORITES QUERIES
    # =====================================================
    
    async def get_favoritos(
        self,
        usuario_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get user's favorite places with place details.
        
        Args:
            usuario_id: User ID
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of favorite places with details
        """
        try:
            result = self.supabase.table("favoritos")\
                .select("*, lugares(*)")\
                .eq("usuario_id", usuario_id)\
                .range(offset, offset + limit - 1)\
                .order("fecha_agregado", desc=True)\
                .execute()
            
            if result.data:
                # Extract place details and add favorite metadata
                favorites = []
                for fav in result.data:
                    place = fav.get("lugares", {})
                    if place:
                        place["favorito_id"] = fav.get("id")
                        place["fecha_agregado"] = fav.get("fecha_agregado")
                        favorites.append(place)
                return favorites
            
            return []
            
        except Exception as e:
            self._handle_error(e, "get_favoritos", usuario_id=usuario_id)
            return []
    
    async def add_favorito(
        self,
        usuario_id: str,
        lugar_id: int
    ) -> bool:
        """
        Add a place to user's favorites.
        
        Args:
            usuario_id: User ID
            lugar_id: Place ID
        
        Returns:
            True if added, False if already exists
        """
        try:
            # Check if already exists
            existing = self.supabase.table("favoritos")\
                .select("id")\
                .eq("usuario_id", usuario_id)\
                .eq("lugar_id", lugar_id)\
                .execute()
            
            if existing.data and len(existing.data) > 0:
                return False
            
            # Add to favorites
            data = {
                "usuario_id": usuario_id,
                "lugar_id": lugar_id,
                "fecha_agregado": datetime.now().isoformat()
            }
            
            self.supabase.table("favoritos").insert(data).execute()
            
            # Update user profile total_favoritos (optional)
            await self._increment_favoritos_count(usuario_id)
            
            logger.info(f"Added place {lugar_id} to favorites for user {usuario_id}")
            return True
            
        except Exception as e:
            self._handle_error(e, "add_favorito", usuario_id=usuario_id, lugar_id=lugar_id)
            return False
    
    async def remove_favorito(
        self,
        usuario_id: str,
        lugar_id: int
    ) -> bool:
        """
        Remove a place from user's favorites.
        
        Args:
            usuario_id: User ID
            lugar_id: Place ID
        
        Returns:
            True if removed, False if not found
        """
        try:
            result = self.supabase.table("favoritos")\
                .delete()\
                .eq("usuario_id", usuario_id)\
                .eq("lugar_id", lugar_id)\
                .execute()
            
            removed = result.data and len(result.data) > 0
            
            if removed:
                # Update user profile total_favoritos (optional)
                await self._decrement_favoritos_count(usuario_id)
                logger.info(f"Removed place {lugar_id} from favorites for user {usuario_id}")
            
            return removed
            
        except Exception as e:
            self._handle_error(e, "remove_favorito", usuario_id=usuario_id, lugar_id=lugar_id)
            return False
    
    async def is_favorito(
        self,
        usuario_id: str,
        lugar_id: int
    ) -> bool:
        """
        Check if a place is in user's favorites.
        
        Args:
            usuario_id: User ID
            lugar_id: Place ID
        
        Returns:
            True if favorite, False otherwise
        """
        try:
            result = self.supabase.table("favoritos")\
                .select("id")\
                .eq("usuario_id", usuario_id)\
                .eq("lugar_id", lugar_id)\
                .limit(1)\
                .execute()
            
            return result.data is not None and len(result.data) > 0
            
        except Exception:
            return False
    
    async def _increment_favoritos_count(self, usuario_id: str) -> None:
        """Increment user's favoritos count."""
        try:
            user = await self.get_by_id(usuario_id, id_column="id")
            if user:
                current = user.get("total_favoritos", 0)
                await self.update(
                    usuario_id,
                    {"total_favoritos": current + 1},
                    id_column="id"
                )
        except Exception:
            pass
    
    async def _decrement_favoritos_count(self, usuario_id: str) -> None:
        """Decrement user's favoritos count."""
        try:
            user = await self.get_by_id(usuario_id, id_column="id")
            if user:
                current = user.get("total_favoritos", 0)
                await self.update(
                    usuario_id,
                    {"total_favoritos": max(0, current - 1)},
                    id_column="id"
                )
        except Exception:
            pass
    
    # =====================================================
    # USER STATISTICS
    # =====================================================
    
    async def get_user_stats(
        self,
        usuario_id: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive user statistics.
        
        Args:
            usuario_id: User ID
        
        Returns:
            Dictionary with user statistics
        """
        try:
            # Get routes created
            rutas = self.supabase.table("rutas_usuario")\
                .select("id, completada")\
                .eq("usuario_id", usuario_id)\
                .execute()
            
            total_rutas = len(rutas.data or [])
            rutas_completadas = sum(1 for r in (rutas.data or []) if r.get("completada"))
            
            # Get favorites
            favoritos = await self.get_favoritos(usuario_id, limit=1000)
            
            # Get reviews
            resenas = self.supabase.table("resenas")\
                .select("rating")\
                .eq("usuario_id", usuario_id)\
                .execute()
            
            total_resenas = len(resenas.data or [])
            avg_rating = 0
            if resenas.data:
                avg_rating = sum(r.get("rating", 0) for r in resenas.data) / len(resenas.data)
            
            # Get interests distribution
            intereses = await self.get_intereses(usuario_id)
            
            return {
                "usuario_id": usuario_id,
                "total_rutas": total_rutas,
                "rutas_completadas": rutas_completadas,
                "total_favoritos": len(favoritos),
                "total_resenas": total_resenas,
                "rating_promedio": round(avg_rating, 1),
                "intereses": intereses,
                "intereses_count": len(intereses),
                "lugares_favoritos": favoritos[:5]  # Top 5 favorites
            }
            
        except Exception as e:
            self._handle_error(e, "get_user_stats", usuario_id=usuario_id)
            return {}
    
    async def get_top_users(
        self,
        limit: int = 10,
        by: str = "total_rutas"
    ) -> List[Dict[str, Any]]:
        """
        Get top users by activity.
        
        Args:
            limit: Maximum number of users
            by: Metric to sort by (total_rutas, total_favoritos, total_resenas)
        
        Returns:
            List of top users
        """
        valid_metrics = ["total_rutas", "total_favoritos", "total_resenas"]
        if by not in valid_metrics:
            raise ValueError(f"Invalid metric. Use one of: {valid_metrics}")
        
        try:
            result = self._table.select("*")\
                .eq("activo", True)\
                .order(by, desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "get_top_users", limit=limit, by=by)
            return []
    
    # =====================================================
    # USER PREFERENCES
    # =====================================================
    
    async def update_preferences(
        self,
        usuario_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user preferences.
        
        Args:
            usuario_id: User ID
            preferences: Dictionary with preference fields
        
        Returns:
            Updated user profile
        """
        allowed_fields = [
            "idioma", "tema", "notificaciones_email", "notificaciones_push",
            "compartir_ubicacion", "latitud", "longitud"
        ]
        
        # Filter only allowed fields
        update_data = {k: v for k, v in preferences.items() if k in allowed_fields}
        
        if not update_data:
            return await self.get_by_id_or_fail(usuario_id, id_column="id")
        
        return await self.update(usuario_id, update_data, id_column="id")


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("UsuarioRepository module loaded successfully")
    print("\nAvailable custom methods:")
    methods = [
        "get_by_email()",
        "get_or_create_by_auth_id()",
        "update_last_login()",
        "get_profile_with_stats()",
        "get_intereses()",
        "set_intereses()",
        "add_interes()",
        "remove_interes()",
        "get_favoritos()",
        "add_favorito()",
        "remove_favorito()",
        "is_favorito()",
        "get_user_stats()",
        "get_top_users()",
        "update_preferences()"
    ]
    for method in methods:
        print(f"  - {method}")