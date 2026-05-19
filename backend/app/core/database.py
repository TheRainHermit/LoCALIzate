"""
Database module for LoCALIzate Backend
=====================================

Manages Supabase client connections and database operations.
Provides both anonymous and admin (service role) clients.

Usage:
    from core.database import get_db, get_supabase_admin, init_db
    
    # Get client for normal operations (RLS applies)
    supabase = get_db()
    
    # Get admin client (bypasses RLS)
    supabase_admin = get_supabase_admin()
"""

import logging
from typing import Optional
from functools import lru_cache

from supabase import create_client, Client
from postgrest.exceptions import APIError

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class SupabaseClientManager:
    """
    Singleton manager for Supabase clients.
    Handles both anonymous and service role clients.
    """
    
    _instance: Optional['SupabaseClientManager'] = None
    _client: Optional[Client] = None
    _admin_client: Optional[Client] = None
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the manager."""
        self._initialized = False
    
    def _initialize(self):
        """Lazy initialization of clients."""
        if self._initialized:
            return
        
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
            )
        
        logger.info(f"Initializing Supabase client for {settings.APP_ENV} environment")
        self._initialized = True
    
    @property
    def client(self) -> Client:
        """
        Get the anonymous Supabase client.
        Respects Row Level Security (RLS) policies.
        """
        self._initialize()
        if self._client is None:
            self._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.debug("Anonymous Supabase client created")
        return self._client
    
    @property
    def admin_client(self) -> Client:
        """
        Get the admin Supabase client with service role.
        Bypasses RLS - use with caution!
        """
        self._initialize()
        if self._admin_client is None:
            if not settings.SUPABASE_SERVICE_KEY:
                raise ValueError(
                    "SUPABASE_SERVICE_KEY required for admin operations"
                )
            self._admin_client = create_client(
                settings.SUPABASE_URL, 
                settings.SUPABASE_SERVICE_KEY
            )
            logger.debug("Admin Supabase client created")
        return self._admin_client


# Global manager instance
_manager = SupabaseClientManager()


def get_db() -> Client:
    """
    Dependency injection for Supabase client.
    Returns anonymous client (respects RLS).
    
    Usage:
        @app.get("/lugares")
        async def get_lugares(supabase: Client = Depends(get_db)):
            result = supabase.table("lugares").select("*").execute()
            return result.data
    """
    return _manager.client


def get_supabase_admin() -> Client:
    """
    Get admin client with service role.
    Bypasses RLS - only use for admin operations!
    
    Usage:
        @app.post("/admin/lugares")
        async def create_lugar(supabase_admin: Client = Depends(get_supabase_admin)):
            # Admin operations here
    """
    return _manager.admin_client


def get_supabase_client() -> Client:
    """
    Alias for get_db() for backward compatibility.
    """
    return get_db()


async def init_db() -> bool:
    """
    Initialize database connection and verify connectivity.
    Should be called on application startup.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        logger.info("Testing Supabase connection...")
        
        # Try to execute a simple query
        result = get_db().table("categorias").select("count", count="exact").limit(1).execute()
        
        logger.info("✅ Supabase connection successful")
        logger.info(f"   Environment: {settings.APP_ENV}")
        logger.info(f"   URL: {settings.SUPABASE_URL}")
        
        return True
        
    except APIError as e:
        logger.error(f"❌ Supabase API Error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {str(e)}")
        return False


async def close_db() -> None:
    """
    Close database connections.
    Called on application shutdown.
    """
    logger.info("Closing Supabase connections...")
    # Supabase client doesn't require explicit closing
    # But we clear the cached instances
    global _manager
    _manager._client = None
    _manager._admin_client = None
    _manager._initialized = False
    logger.debug("Supabase clients cleared")


def check_connection() -> dict:
    """
    Check database connection status.
    Useful for health check endpoints.
    
    Returns:
        dict: Connection status information
    """
    try:
        supabase = get_db()
        # Intentar una consulta simple que funcione siempre
        result = supabase.table("categorias").select("*", count="exact").limit(1).execute()
        
        # Usar getattr para acceder al count de forma segura
        count_result = getattr(result, 'count', 0)
        
        return {
            "status": "connected",
            "environment": settings.APP_ENV,
            "supabase_url": settings.SUPABASE_URL[:30] + "..." if settings.SUPABASE_URL else None,
            "records": count_result
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e),
            "environment": settings.APP_ENV
        }


# =====================================================
# HELPER FUNCTIONS FOR COMMON OPERATIONS
# =====================================================

def execute_query(table: str, query_builder):
    """
    Execute a query with error handling.
    
    Args:
        table: Table name
        query_builder: Function that builds the query
    
    Returns:
        tuple: (data, error) - error is None if successful
    """
    try:
        supabase = get_db()
        result = query_builder(supabase.table(table)).execute()
        return result.data, None
    except APIError as e:
        logger.error(f"Query error on {table}: {str(e)}")
        return None, str(e)
    except Exception as e:
        logger.error(f"Unexpected error on {table}: {str(e)}")
        return None, str(e)


async def execute_query_async(table: str, query_builder):
    """
    Async wrapper for execute_query.
    """
    return execute_query(table, query_builder)


def get_by_id(table: str, id_value, id_column: str = "id"):
    """
    Get a record by ID.
    
    Args:
        table: Table name
        id_value: ID value to search for
        id_column: Column name (default: "id")
    
    Returns:
        tuple: (data, error)
    """
    try:
        supabase = get_db()
        result = supabase.table(table).select("*").eq(id_column, id_value).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0], None
        return None, None
    except APIError as e:
        logger.error(f"Error getting by ID from {table}: {str(e)}")
        return None, str(e)


def insert_record(table: str, data: dict):
    """
    Insert a single record.
    
    Args:
        table: Table name
        data: Record data
    
    Returns:
        tuple: (inserted_record, error)
    """
    try:
        supabase = get_db()
        result = supabase.table(table).insert(data).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0], None
        return None, None
    except APIError as e:
        logger.error(f"Error inserting into {table}: {str(e)}")
        return None, str(e)


def update_record(table: str, id_value, data: dict, id_column: str = "id"):
    """
    Update a record by ID.
    
    Args:
        table: Table name
        id_value: ID value
        data: Updated data
        id_column: Column name (default: "id")
    
    Returns:
        tuple: (updated_record, error)
    """
    try:
        supabase = get_db()
        result = supabase.table(table).update(data).eq(id_column, id_value).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0], None
        return None, None
    except APIError as e:
        logger.error(f"Error updating {table}: {str(e)}")
        return None, str(e)


def delete_record(table: str, id_value, id_column: str = "id"):
    """
    Delete a record by ID.
    
    Args:
        table: Table name
        id_value: ID value
        id_column: Column name (default: "id")
    
    Returns:
        tuple: (deleted_record, error)
    """
    try:
        supabase = get_db()
        result = supabase.table(table).delete().eq(id_column, id_value).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0], None
        return None, None
    except APIError as e:
        logger.error(f"Error deleting from {table}: {str(e)}")
        return None, str(e)


# =====================================================
# CONTEXT MANAGER FOR TRANSACTIONS
# =====================================================

class Transaction:
    """
    Simple context manager for database operations.
    Note: Supabase doesn't support traditional transactions,
    this is just for API consistency.
    """
    
    def __init__(self, supabase: Client = None):
        self.supabase = supabase or get_db()
        self.operations = []
    
    def add(self, operation):
        """Add an operation to the transaction."""
        self.operations.append(operation)
        return self
    
    async def commit(self):
        """Execute all operations."""
        results = []
        errors = []
        
        for op in self.operations:
            try:
                result = await op(self.supabase)
                results.append(result)
            except Exception as e:
                errors.append(str(e))
        
        return results, errors
    
    async def rollback(self):
        """Clear operations (no actual rollback in Supabase)."""
        self.operations = []
        return True


# =====================================================
# HEALTH CHECK
# =====================================================

async def health_check() -> dict:
    """
    Comprehensive health check for database.
    """
    return {
        "database": check_connection(),
        "config": {
            "environment": settings.APP_ENV,
            "supabase_url": settings.SUPABASE_URL[:30] + "..." if settings.SUPABASE_URL else None
        }
    }


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_connection():
        print("Testing database connection...")
        result = await init_db()
        print(f"Connection test: {'✅ PASS' if result else '❌ FAIL'}")
        
        if result:
            health = health_check()
            print(f"Health check: {health}")
    
    asyncio.run(test_connection())