"""
Evento Repository for LoCALIzate Backend
=======================================

Repository for events and festivals in Cali.
Provides specialized queries for events including:
    - Upcoming events (fecha_inicio >= today)
    - Events by date range
    - Featured events
    - Events by location
    - Recurring events (weekly, monthly, etc.)
    - Search by name/description/tags

Inherits from BaseRepository for common CRUD operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import logging

from supabase import Client
from app.repositories.base_repo import BaseRepository
from app.core.exceptions import DatabaseException

# Configure logging
logger = logging.getLogger(__name__)


class EventoRepository(BaseRepository):
    """
    Repository for events and festivals in Cali.
    
    Attributes:
        supabase: Supabase client instance
        table_name: "eventos" (table name in Supabase)
    """
    
    def __init__(self, supabase: Client):
        """Initialize repository with 'eventos' table."""
        super().__init__(supabase, "eventos")
    
    # =====================================================
    # DATE-BASED QUERIES
    # =====================================================
    
    async def get_upcoming(
        self,
        limit: int = 20,
        offset: int = 0,
        desde: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming events (fecha_inicio >= today or specified date).
        
        Args:
            limit: Maximum number of records
            offset: Number of records to skip
            desde: Optional custom start date (defaults to today)
        
        Returns:
            List of upcoming events sorted by fecha_inicio
        """
        try:
            start_date = desde or date.today()
            start_date_str = start_date.isoformat()
            
            result = self._table.select("*")\
                .gte("fecha_inicio", start_date_str)\
                .eq("activo", True)\
                .order("fecha_inicio")\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "get_upcoming", desde=desde, limit=limit)
            return []
    
    async def get_ongoing(
        self,
        today: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get events currently happening (fecha_inicio <= today <= fecha_fin).
        
        Args:
            today: Optional custom date (defaults to today)
        
        Returns:
            List of ongoing events
        """
        try:
            current_date = today or date.today()
            current_date_str = current_date.isoformat()
            
            result = self._table.select("*")\
                .lte("fecha_inicio", current_date_str)\
                .gte("fecha_fin", current_date_str)\
                .eq("activo", True)\
                .order("fecha_inicio")\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "get_ongoing", today=today)
            return []
    
    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get events within a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of events in the date range
        """
        try:
            start_str = start_date.isoformat()
            end_str = end_date.isoformat()
            
            result = self._table.select("*")\
                .gte("fecha_inicio", start_str)\
                .lte("fecha_inicio", end_str)\
                .eq("activo", True)\
                .order("fecha_inicio")\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "get_by_date_range", start_date=start_date, end_date=end_date)
            return []
    
    async def get_by_month(
        self,
        year: int,
        month: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get events in a specific month.
        
        Args:
            year: Year (e.g., 2026)
            month: Month (1-12)
            limit: Maximum number of records
        
        Returns:
            List of events in that month
        """
        try:
            start_date = date(year, month, 1)
            
            # Calculate end date (last day of month)
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            return await self.get_by_date_range(start_date, end_date, limit=limit)
            
        except Exception as e:
            self._handle_error(e, "get_by_month", year=year, month=month)
            return []
    
    async def get_today(self) -> List[Dict[str, Any]]:
        """
        Get events happening today.
        
        Returns:
            List of today's events
        """
        today_date = date.today()
        return await self.get_by_date_range(today_date, today_date)
    
    async def get_tomorrow(self) -> List[Dict[str, Any]]:
        """
        Get events happening tomorrow.
        
        Returns:
            List of tomorrow's events
        """
        tomorrow_date = date.today() + timedelta(days=1)
        return await self.get_by_date_range(tomorrow_date, tomorrow_date)
    
    async def get_this_week(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get events happening this week (from today to next 7 days).
        
        Args:
            limit: Maximum number of records
        
        Returns:
            List of events this week
        """
        today_date = date.today()
        next_week = today_date + timedelta(days=7)
        return await self.get_by_date_range(today_date, next_week, limit=limit)
    
    async def get_this_month(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get events happening this month.
        
        Args:
            limit: Maximum number of records
        
        Returns:
            List of events this month
        """
        today_date = date.today()
        # Get first day of next month
        if today_date.month == 12:
            next_month = date(today_date.year + 1, 1, 1)
        else:
            next_month = date(today_date.year, today_date.month + 1, 1)
        
        return await self.get_by_date_range(today_date, next_month - timedelta(days=1), limit=limit)
    
    # =====================================================
    # SPECIALIZED QUERIES
    # =====================================================
    
    async def get_destacados(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get featured events (destacado = True).
        
        Args:
            limit: Maximum number of records
        
        Returns:
            List of featured events
        """
        return await self.get_all(
            filters={"destacado": True, "activo": True},
            limit=limit,
            order_by="fecha_inicio"
        )
    
    async def get_by_tags(
        self,
        tags: List[str],
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get events by tags (any matching tag).
        
        Args:
            tags: List of tag strings to search for
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of events matching any of the tags
        """
        try:
            # Build query for tags (Supabase array contains)
            query = self._table.select("*").eq("activo", True)
            
            # Add condition for each tag
            for tag in tags:
                query = query.contains("tags", [tag])
            
            result = query.order("fecha_inicio")\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "get_by_tags", tags=tags)
            return []
    
    async def search_eventos(
        self,
        search_term: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search events by name or description.
        
        Args:
            search_term: Text to search for
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of matching events
        """
        try:
            result = self._table.select("*")\
                .or_(f"nombre.ilike.%{search_term}%,descripcion.ilike.%{search_term}%")\
                .eq("activo", True)\
                .order("fecha_inicio")\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "search_eventos", search_term=search_term)
            return []
    
    async def get_by_ubicacion(
        self,
        ubicacion: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get events by location name.
        
        Args:
            ubicacion: Location name
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of events at that location
        """
        return await self.get_all(
            filters={"ubicacion": ubicacion, "activo": True},
            limit=limit,
            offset=offset,
            order_by="fecha_inicio"
        )
    
    async def get_gratis(
        self,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get free events (precio contains 'Gratis').
        
        Args:
            limit: Maximum number of records
        
        Returns:
            List of free events
        """
        try:
            result = self._table.select("*")\
                .eq("activo", True)\
                .or_(f"precio.ilike.%Gratis%,precio.ilike.%Gratuito%")\
                .order("fecha_inicio")\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "get_gratis")
            return []
    
    async def get_recurrentes(
        self,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get recurring events (es_recurrente = True).
        
        Args:
            limit: Maximum number of records
        
        Returns:
            List of recurring events
        """
        return await self.get_all(
            filters={"es_recurrente": True, "activo": True},
            limit=limit,
            order_by="frecuencia"
        )
    
    # =====================================================
    # STATISTICS & AGGREGATION
    # =====================================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get event statistics.
        
        Returns:
            Dictionary with event statistics
        """
        try:
            # Get total count
            total = await self.get_count(filters={"activo": True})
            
            # Get upcoming count
            upcoming = await self.get_count(
                filters={"activo": True, "fecha_inicio": date.today().isoformat()}
            )
            
            # Get by category
            result = self._table.select("tags", count="exact").eq("activo", True).execute()
            
            # Count tags occurrences
            tag_counts = {}
            for event in (result.data or []):
                tags = event.get("tags", [])
                if tags:
                    for tag in tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Get top 5 tags
            top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "total_eventos": total,
                "proximos_eventos": upcoming,
                "eventos_por_tag": dict(top_tags),
                "recurrentes": await self.get_count(filters={"es_recurrente": True, "activo": True})
            }
            
        except Exception as e:
            self._handle_error(e, "get_stats")
            return {}
    
    async def get_calendar_month(
        self,
        year: int,
        month: int
    ) -> Dict[int, List[Dict[str, Any]]]:
        """
        Get events grouped by day for a specific month.
        
        Args:
            year: Year (e.g., 2026)
            month: Month (1-12)
        
        Returns:
            Dictionary with day numbers as keys and list of events as values
        """
        events = await self.get_by_month(year, month, limit=200)
        
        calendar = {}
        for event in events:
            event_date = datetime.fromisoformat(event["fecha_inicio"]).date()
            day = event_date.day
            
            if day not in calendar:
                calendar[day] = []
            calendar[day].append(event)
        
        return calendar
    
    # =====================================================
    # VALIDATION & EXISTENCE
    # =====================================================
    
    async def exists_by_name_and_date(
        self,
        nombre: str,
        fecha_inicio: date
    ) -> bool:
        """
        Check if an event with same name and start date already exists.
        
        Args:
            nombre: Event name
            fecha_inicio: Start date
        
        Returns:
            True if exists, False otherwise
        """
        try:
            result = self._table.select("id")\
                .eq("nombre", nombre)\
                .eq("fecha_inicio", fecha_inicio.isoformat())\
                .limit(1)\
                .execute()
            
            return result.data is not None and len(result.data) > 0
            
        except Exception:
            return False
    
    async def get_upcoming_notification(
        self,
        days_ahead: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get events happening in the next N days (for notifications).
        
        Args:
            days_ahead: Number of days to look ahead
        
        Returns:
            List of upcoming events for notifications
        """
        try:
            today_date = date.today()
            future_date = today_date + timedelta(days=days_ahead)
            
            return await self.get_by_date_range(today_date, future_date, limit=100)
            
        except Exception as e:
            self._handle_error(e, "get_upcoming_notification", days_ahead=days_ahead)
            return []


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("EventoRepository module loaded successfully")
    print("\nAvailable custom methods:")
    methods = [
        "get_upcoming()",
        "get_ongoing()",
        "get_by_date_range()",
        "get_by_month()",
        "get_today()",
        "get_tomorrow()",
        "get_this_week()",
        "get_this_month()",
        "get_destacados()",
        "get_by_tags()",
        "search_eventos()",
        "get_by_ubicacion()",
        "get_gratis()",
        "get_recurrentes()",
        "get_stats()",
        "get_calendar_month()",
        "exists_by_name_and_date()",
        "get_upcoming_notification()"
    ]
    for method in methods:
        print(f"  - {method}")