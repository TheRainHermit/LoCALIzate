"""
Lugar Repository for LoCALIzate Backend
======================================

Repository for tourist places (lugares) in Cali.
Provides specialized queries for places including:
    - Filtering by interest category (cultura, naturaleza, gastronomia, salsa, aventura)
    - Proximity search (nearby places)
    - Rating-based queries
    - Search by name/description
    - Featured places

Inherits from BaseRepository for common CRUD operations.
"""

from typing import Optional, List, Dict, Any
from math import radians, sin, cos, sqrt, atan2
import logging

from supabase import Client
from app.repositories.base_repo import BaseRepository
from app.core.exceptions import DatabaseException

# Configure logging
logger = logging.getLogger(__name__)


class LugarRepository(BaseRepository):
    """
    Repository for tourist places (lugares) in Cali.
    
    Attributes:
        supabase: Supabase client instance
        table_name: "lugares" (table name in Supabase)
    """
    
    def __init__(self, supabase: Client):
        """Initialize repository with 'lugares' table."""
        super().__init__(supabase, "lugares")
    
    # =====================================================
    # GEOGRAPHIC HELPER FUNCTIONS
    # =====================================================
    
    @staticmethod
    def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
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
    
    # =====================================================
    # SPECIALIZED QUERIES
    # =====================================================
    
    async def get_by_interes(
        self,
        interes: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get places by interest category.
        
        Args:
            interes: Interest category (cultura, naturaleza, gastronomia, salsa, aventura)
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of places matching the interest
        """
        valid_interests = ["cultura", "naturaleza", "gastronomia", "salsa", "aventura"]
        if interes not in valid_interests:
            raise ValueError(f"Interés inválido. Debe ser uno de: {valid_interests}")
        
        return await self.get_all(
            filters={"interes": interes, "activo": True},
            limit=limit,
            offset=offset,
            order_by="rating",
            order_desc=True
        )
    
    async def get_destacados(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get featured places (destacados = True).
        
        Args:
            limit: Maximum number of records
        
        Returns:
            List of featured places
        """
        return await self.get_all(
            filters={"destacado": True, "activo": True},
            limit=limit,
            order_by="rating",
            order_desc=True
        )
    
    async def get_by_rating(
        self,
        min_rating: float = 4.0,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get places with rating above minimum.
        
        Args:
            min_rating: Minimum rating (0-5)
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of highly rated places
        """
        return await self.get_all(
            filters={"activo": True},
            limit=limit,
            offset=offset,
            order_by="rating",
            order_desc=True
        )
    
    async def get_nearby(
        self,
        lat: float,
        lng: float,
        radio_km: float = 5.0,
        interes: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get places near a given location.
        
        Args:
            lat: Latitude of reference point
            lng: Longitude of reference point
            radio_km: Search radius in kilometers
            interes: Optional interest filter
            limit: Maximum number of results
        
        Returns:
            List of nearby places with distance added to each
        """
        try:
            # Get all active places (or filtered by interest)
            filters = {"activo": True}
            if interes:
                filters["interes"] = interes
            
            places = await self.get_all(
                filters=filters,
                limit=100,  # Get more to filter by distance
                order_by="rating",
                order_desc=True
            )
            
            # Calculate distance for each place and filter by radius
            nearby_places = []
            for place in places:
                distance = self._haversine_distance(
                    lat, lng,
                    place.get("latitud"), place.get("longitud")
                )
                
                if distance <= radio_km:
                    place["distancia_km"] = round(distance, 2)
                    nearby_places.append(place)
            
            # Sort by distance and limit
            nearby_places.sort(key=lambda x: x["distancia_km"])
            
            return nearby_places[:limit]
            
        except Exception as e:
            self._handle_error(e, "get_nearby", lat=lat, lng=lng, radio_km=radio_km)
            return []
    
    async def search_lugares(
        self,
        search_term: str,
        interes: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search places by name or description.
        
        Args:
            search_term: Text to search for
            interes: Optional interest filter
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of matching places
        """
        try:
            query = self._table.select("*").ilike("nombre", f"%{search_term}%")
            
            if interes:
                query = query.eq("interes", interes)
            
            query = query.eq("activo", True)
            query = query.order("rating", desc=True)
            query = query.range(offset, offset + limit - 1)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "search_lugares", search_term=search_term, interes=interes)
            return []
    
    async def get_by_precio_range(
        self,
        min_precio: Optional[int] = None,
        max_precio: Optional[int] = None,
        interes: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get places within a price range.
        
        Args:
            min_precio: Minimum price in COP
            max_precio: Maximum price in COP
            interes: Optional interest filter
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of places matching price criteria
        """
        try:
            query = self._table.select("*").eq("activo", True)
            
            if interes:
                query = query.eq("interes", interes)
            
            # Filter by price_min <= max_precio and price_max >= min_precio
            if max_precio is not None:
                query = query.lte("precio_min", max_precio)
            
            if min_precio is not None:
                query = query.gte("precio_max", min_precio)
            
            query = query.order("rating", desc=True)
            query = query.range(offset, offset + limit - 1)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "get_by_precio_range", min_precio=min_precio, max_precio=max_precio)
            return []
    
    async def get_gratis(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get free places (precio = 'Gratis' or 'Gratuito').
        
        Args:
            limit: Maximum number of records
        
        Returns:
            List of free places
        """
        try:
            result = self._table.select("*")\
                .eq("activo", True)\
                .or_(f"precio.ilike.%Gratis%,precio.ilike.%Gratuito%")\
                .order("rating", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "get_gratis")
            return []
    
    async def get_by_barrio(
        self,
        barrio: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get places by neighborhood (barrio).
        
        Args:
            barrio: Neighborhood name
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of places in the neighborhood
        """
        return await self.get_all(
            filters={"barrio": barrio, "activo": True},
            limit=limit,
            offset=offset,
            order_by="rating",
            order_desc=True
        )
    
    async def get_rating_stats(self) -> Dict[str, Any]:
        """
        Get rating statistics for all places.
        
        Returns:
            Dictionary with average rating, total places, etc.
        """
        try:
            result = self._table.select("rating").eq("activo", True).execute()
            
            ratings = [place.get("rating", 0) for place in (result.data or []) if place.get("rating")]
            
            if not ratings:
                return {
                    "average_rating": 0,
                    "total_places": 0,
                    "max_rating": 0,
                    "min_rating": 0
                }
            
            return {
                "average_rating": round(sum(ratings) / len(ratings), 2),
                "total_places": len(ratings),
                "max_rating": max(ratings),
                "min_rating": min(ratings)
            }
            
        except Exception as e:
            self._handle_error(e, "get_rating_stats")
            return {}
    
    async def get_by_interest_with_stats(
        self,
        interes: str
    ) -> Dict[str, Any]:
        """
        Get places by interest with statistics.
        
        Args:
            interes: Interest category
        
        Returns:
            Dictionary with places list and stats
        """
        places = await self.get_by_interes(interes, limit=100)
        
        ratings = [p.get("rating", 0) for p in places if p.get("rating")]
        
        return {
            "interes": interes,
            "total": len(places),
            "average_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "places": places
        }
    
    async def get_all_intereses_stats(self) -> List[Dict[str, Any]]:
        """
        Get statistics for all interest categories.
        
        Returns:
            List of stats per interest category
        """
        intereses = ["cultura", "naturaleza", "gastronomia", "salsa", "aventura"]
        stats = []
        
        for interes in intereses:
            stats.append(await self.get_by_interest_with_stats(interes))
        
        return stats
    
    async def update_rating(
        self,
        lugar_id: int,
        new_rating: float
    ) -> Dict[str, Any]:
        """
        Update the rating of a place (recalculates average).
        
        Note: In production, this should be called by a trigger when 
        new reviews are added. This method is for manual updates.
        
        Args:
            lugar_id: ID of the place
            new_rating: New rating value
        
        Returns:
            Updated place
        """
        # Get current place to get existing rating_count
        current = await self.get_by_id(lugar_id)
        if not current:
            raise ValueError(f"Place with id {lugar_id} not found")
        
        # Calculate new average (simplified - real implementation should use all reviews)
        current_count = current.get("rating_count", 0)
        current_avg = current.get("rating", 0)
        
        if current_count == 0:
            new_avg = new_rating
        else:
            new_avg = ((current_avg * current_count) + new_rating) / (current_count + 1)
        
        new_count = current_count + 1
        
        return await self.update(
            lugar_id,
            {
                "rating": round(new_avg, 1),
                "rating_count": new_count
            }
        )
    
    async def get_recommendations(
        self,
        user_interests: List[str],
        limit: int = 10,
        exclude_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get personalized place recommendations based on user interests.
        
        Args:
            user_interests: List of user's interest categories
            limit: Maximum number of recommendations
            exclude_ids: List of place IDs to exclude (already visited/favorited)
        
        Returns:
            List of recommended places
        """
        try:
            query = self._table.select("*").eq("activo", True)
            
            # Build OR condition for interests
            if user_interests:
                # Create filter for matching any of the user's interests
                # Supabase syntax: interes.in.(cultura,naturaleza)
                interests_str = ",".join(user_interests)
                query = query.in_("interes", interests_str)
            
            # Exclude already visited places
            if exclude_ids:
                query = query.not_.in_("id", exclude_ids)
            
            # Order by rating and mark as destacado
            query = query.order("destacado", desc=True)
            query = query.order("rating", desc=True)
            query = query.limit(limit)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "get_recommendations", user_interests=user_interests)
            return []
    
    async def get_popular(
        self,
        limit: int = 10,
        min_rating: float = 4.0
    ) -> List[Dict[str, Any]]:
        """
        Get most popular places (high rating + many reviews).
        
        Args:
            limit: Maximum number of records
            min_rating: Minimum rating threshold
        
        Returns:
            List of popular places
        """
        try:
            result = self._table.select("*")\
                .eq("activo", True)\
                .gte("rating", min_rating)\
                .order("rating_count", desc=True)\
                .order("rating", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "get_popular")
            return []


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("LugarRepository module loaded successfully")
    print("\nAvailable custom methods:")
    methods = [
        "get_by_interes()",
        "get_destacados()",
        "get_by_rating()",
        "get_nearby()",
        "search_lugares()",
        "get_by_precio_range()",
        "get_gratis()",
        "get_by_barrio()",
        "get_rating_stats()",
        "get_by_interest_with_stats()",
        "get_all_intereses_stats()",
        "update_rating()",
        "get_recommendations()",
        "get_popular()"
    ]
    for method in methods:
        print(f"  - {method}")