"""
Base Repository for LoCALIzate / CaliGuia Backend
=================================================

Abstract base class that implements common CRUD operations
for all repositories. Provides a consistent interface for
database interactions using Supabase.

Features:
    - Generic CRUD operations (Create, Read, Update, Delete)
    - Pagination support
    - Filtering and sorting
    - Soft delete support
    - Batch operations
    - Error handling with custom exceptions

Usage:
    class LugarRepository(BaseRepository):
        def __init__(self, supabase_client):
            super().__init__(supabase_client, "lugares")
        
        # Add custom methods here
        async def get_by_interes(self, interes: str):
            return await self.get_all(filters={"interes": interes})
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import logging

from supabase import Client # type: ignore
from postgrest.exceptions import APIError # type: ignore

from app.core.exceptions import (
    DatabaseException,
    NotFoundException,
    DuplicateResourceException
)

# Configure logging
logger = logging.getLogger(__name__)


class BaseRepository:
    """
    Abstract base repository with common CRUD operations.
    
    Attributes:
        supabase: Supabase client instance
        table_name: Name of the database table
    """
    
    def __init__(self, supabase: Client, table_name: str):
        """
        Initialize repository.
        
        Args:
            supabase: Supabase client instance
            table_name: Name of the database table
        """
        self.supabase = supabase
        self.table_name = table_name
        self._table = supabase.table(table_name)
    
    # =====================================================
    # PROTECTED METHODS
    # =====================================================
    
    def _handle_error(self, error: Exception, operation: str, **context) -> None:
        """
        Handle database errors consistently.
        
        Args:
            error: The exception that occurred
            operation: Name of the operation being performed
            **context: Additional context for error message
        
        Raises:
            DatabaseException: Wrapped database error
        """
        logger.error(f"Database error on {operation} for {self.table_name}: {str(error)}")
        logger.debug(f"Context: {context}")
        
        # Check for duplicate key error
        if "duplicate key" in str(error).lower():
            raise DuplicateResourceException(
                resource_type=self.table_name,
                field=context.get("field", "unknown"),
                value=context.get("value", "unknown"),
                metadata={"operation": operation, "error": str(error)}
            )
        
        # Check for not found
        if "not found" in str(error).lower() or "no rows" in str(error).lower():
            raise NotFoundException(
                resource_type=self.table_name,
                metadata={"operation": operation, "error": str(error)}
            )
        
        # Generic database error
        raise DatabaseException(
            detail=f"Error en operación {operation} en {self.table_name}",
            operation=operation,
            table=self.table_name,
            original_error=str(error),
            metadata=context
        )
    
    def _build_query(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Build a query with filters.
        
        Args:
            filters: Dictionary of filters (column=value)
        
        Returns:
            Query builder with filters applied
        """
        query = self._table.select("*")
        
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.eq(key, value)
        
        return query
    
    def _build_query_with_pagination(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> Any:
        """
        Build a query with filters and pagination.
        
        Args:
            filters: Dictionary of filters
            limit: Maximum number of records
            offset: Number of records to skip
            order_by: Column to order by
            order_desc: True for descending, False for ascending
        
        Returns:
            Query builder with filters and pagination applied
        """
        query = self._build_query(filters)
        
        if order_by:
            query = query.order(order_by, desc=order_desc)
        
        query = query.range(offset, offset + limit - 1)
        
        return query
    
    # =====================================================
    # CRUD OPERATIONS
    # =====================================================
    
    async def get_by_id(
        self,
        id_value: Union[int, str],
        id_column: str = "id"
    ) -> Optional[Dict[str, Any]]:
        """
        Get a record by its ID.
        
        Args:
            id_value: ID value to search for
            id_column: Column name (default: "id")
        
        Returns:
            Record data or None if not found
        
        Raises:
            DatabaseException: On database error
        """
        try:
            result = self._table.select("*").eq(id_column, id_value).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            self._handle_error(e, "get_by_id", id=id_value, id_column=id_column)
            return None
    
    async def get_by_id_or_fail(
        self,
        id_value: Union[int, str],
        id_column: str = "id"
    ) -> Dict[str, Any]:
        """
        Get a record by ID or raise NotFoundException.
        
        Args:
            id_value: ID value to search for
            id_column: Column name (default: "id")
        
        Returns:
            Record data
        
        Raises:
            NotFoundException: If record not found
            DatabaseException: On database error
        """
        result = await self.get_by_id(id_value, id_column)
        
        if not result:
            raise NotFoundException(
                resource_type=self.table_name,
                resource_id=id_value,
                metadata={"id_column": id_column}
            )
        
        return result
    
    async def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all records matching filters.
        
        Args:
            filters: Dictionary of filters
            limit: Maximum number of records
            offset: Number of records to skip
            order_by: Column to order by
            order_desc: True for descending, False for ascending
        
        Returns:
            List of records
        """
        try:
            query = self._build_query_with_pagination(
                filters=filters,
                limit=limit,
                offset=offset,
                order_by=order_by,
                order_desc=order_desc
            )
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error en get_all: {str(e)}")
            return []
    
    async def get_count(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Get count of records matching filters.
        
        Args:
            filters: Dictionary of filters
        
        Returns:
            Number of records
        """
        try:
            query = self._build_query(filters)
            
            # Método 1: usar count con select
            try:
                result = query.select("*", count="exact").limit(0).execute()
                count = getattr(result, 'count', None)
                if count is not None:
                    return count
            except Exception as e1:
                logger.debug(f"Método 1 falló: {str(e1)}")
            
            # Método 2: contar resultados reales (limitado)
            try:
                result = query.limit(1000).execute()
                return len(result.data) if result.data else 0
            except Exception as e2:
                logger.debug(f"Método 2 falló: {str(e2)}")
            
            # Método 3: consulta separada solo para count
            try:
                result = self.supabase.table(self.table_name).select("id", count="exact").execute()
                return getattr(result, 'count', 0)
            except Exception as e3:
                logger.debug(f"Método 3 falló: {str(e3)}")
            
            return 0
            
        except Exception as e:
            logger.error(f"Error en get_count: {str(e)}")
            return 0
    
    async def create(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new record.
        
        Args:
            data: Record data to insert
        
        Returns:
            Created record
        
        Raises:
            DuplicateResourceException: On duplicate key
            DatabaseException: On other database errors
        """
        try:
            # Add timestamps if not provided
            if "created_at" not in data:
                data["created_at"] = datetime.now().isoformat()
            
            result = self._table.insert(data).execute()
            
            if result.data and len(result.data) > 0:
                logger.debug(f"Created record in {self.table_name}: {result.data[0].get('id')}")
                return result.data[0]
            
            raise DatabaseException(
                detail=f"No se pudo crear el registro en {self.table_name}",
                operation="create",
                table=self.table_name
            )
            
        except Exception as e:
            self._handle_error(e, "create", data=data)
            raise
    
    async def create_batch(
        self,
        items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create multiple records in batch.
        
        Args:
            items: List of record data to insert
        
        Returns:
            List of created records
        """
        try:
            # Add timestamps
            for item in items:
                if "created_at" not in item:
                    item["created_at"] = datetime.now().isoformat()
            
            result = self._table.insert(items).execute()
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "create_batch", count=len(items))
            return []
    
    async def update(
        self,
        id_value: Union[int, str],
        data: Dict[str, Any],
        id_column: str = "id"
    ) -> Dict[str, Any]:
        """
        Update a record by ID.
        
        Args:
            id_value: ID value to update
            data: Updated data
            id_column: Column name (default: "id")
        
        Returns:
            Updated record
        
        Raises:
            NotFoundException: If record not found
            DatabaseException: On database error
        """
        try:
            # Add updated timestamp
            data["updated_at"] = datetime.now().isoformat()
            
            result = self._table.update(data).eq(id_column, id_value).execute()
            
            if result.data and len(result.data) > 0:
                logger.debug(f"Updated record in {self.table_name}: {id_value}")
                return result.data[0]
            
            raise NotFoundException(
                resource_type=self.table_name,
                resource_id=id_value,
                metadata={"id_column": id_column}
            )
            
        except NotFoundException:
            raise
        except Exception as e:
            self._handle_error(e, "update", id=id_value, data=data, id_column=id_column)
            raise
    
    async def update_batch(
        self,
        updates: List[Dict[str, Any]],
        id_column: str = "id"
    ) -> List[Dict[str, Any]]:
        """
        Update multiple records in batch.
        
        Args:
            updates: List of dicts each containing 'id' and update data
            id_column: Column name for ID (default: "id")
        
        Returns:
            List of updated records
        """
        results = []
        errors = []
        
        for update_item in updates:
            try:
                id_value = update_item.pop(id_column)
                data = update_item
                result = await self.update(id_value, data, id_column)
                results.append(result)
            except Exception as e:
                errors.append({"id": update_item.get(id_column), "error": str(e)})
        
        if errors:
            logger.warning(f"Batch update had {len(errors)} errors: {errors}")
        
        return results
    
    async def delete(
        self,
        id_value: Union[int, str],
        id_column: str = "id",
        soft_delete: bool = True
    ) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id_value: ID value to delete
            id_column: Column name (default: "id")
            soft_delete: If True, sets 'activo' to False instead of hard delete
        
        Returns:
            True if deleted, False otherwise
        
        Raises:
            NotFoundException: If record not found
            DatabaseException: On database error
        """
        try:
            if soft_delete:
                # Check if 'activo' column exists
                result = await self.update(id_value, {"activo": False}, id_column)
                return result is not None
            else:
                # Hard delete
                result = self._table.delete().eq(id_column, id_value).execute()
                deleted = result.data and len(result.data) > 0
                
                if deleted:
                    logger.debug(f"Hard deleted record from {self.table_name}: {id_value}")
                
                return deleted
                
        except NotFoundException:
            raise
        except Exception as e:
            self._handle_error(e, "delete", id=id_value, id_column=id_column, soft_delete=soft_delete)
            return False
    
    async def delete_batch(
        self,
        ids: List[Union[int, str]],
        id_column: str = "id",
        soft_delete: bool = True
    ) -> int:
        """
        Delete multiple records in batch.
        
        Args:
            ids: List of IDs to delete
            id_column: Column name for ID
            soft_delete: If True, sets 'activo' to False instead of hard delete
        
        Returns:
            Number of successfully deleted records
        """
        deleted_count = 0
        
        for id_value in ids:
            try:
                success = await self.delete(id_value, id_column, soft_delete)
                if success:
                    deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to delete {id_value}: {str(e)}")
        
        return deleted_count
    
    # =====================================================
    # UTILITY METHODS
    # =====================================================
    
    async def exists(
        self,
        id_value: Union[int, str],
        id_column: str = "id"
    ) -> bool:
        """
        Check if a record exists.
        
        Args:
            id_value: ID value to check
            id_column: Column name (default: "id")
        
        Returns:
            True if record exists, False otherwise
        """
        try:
            result = self._table.select(id_column).eq(id_column, id_value).limit(1).execute()
            return result.data is not None and len(result.data) > 0
        except Exception:
            return False
    
    async def get_by_field(
        self,
        field: str,
        value: Any,
        limit: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get records by a specific field value.
        
        Args:
            field: Column name
            value: Value to match
            limit: Maximum number of records
        
        Returns:
            List of matching records
        """
        try:
            result = self._table.select("*").eq(field, value).limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            self._handle_error(e, "get_by_field", field=field, value=value, limit=limit)
            return []
    
    async def get_by_multiple_fields(
        self,
        conditions: Dict[str, Any],
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get records by multiple field conditions (AND logic).
        
        Args:
            conditions: Dictionary of field=value conditions
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of matching records
        """
        try:
            query = self._table.select("*")
            
            for field, value in conditions.items():
                if value is not None:
                    query = query.eq(field, value)
            
            result = query.range(offset, offset + limit - 1).execute()
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "get_by_multiple_fields", conditions=conditions)
            return []
    
    async def search(
        self,
        search_column: str,
        search_term: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search records using ILIKE pattern matching.
        
        Args:
            search_column: Column to search in
            search_term: Search term (will be wrapped with %)
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of matching records
        """
        try:
            result = self._table.select("*")\
                .ilike(search_column, f"%{search_term}%")\
                .range(offset, offset + limit - 1)\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            self._handle_error(e, "search", search_column=search_column, search_term=search_term)
            return []
    
    async def get_all_active(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all active records (activo = True).
        
        Args:
            limit: Maximum number of records
            offset: Number of records to skip
            order_by: Column to order by
            order_desc: True for descending
        
        Returns:
            List of active records
        """
        return await self.get_all(
            filters={"activo": True},
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_desc=order_desc
        )
    
    # =====================================================
    # PAGINATION HELPER
    # =====================================================
    
    async def get_page(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> Dict[str, Any]:
        """
        Get a paginated page of results.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            filters: Dictionary of filters
            order_by: Column to order by
            order_desc: True for descending
        
        Returns:
            Dict with 'items', 'total', 'page', 'page_size', 'total_pages'
        """
        offset = (page - 1) * page_size
        
        # Get items for current page
        items = await self.get_all(
            filters=filters,
            limit=page_size,
            offset=offset,
            order_by=order_by,
            order_desc=order_desc
        )
        
        # Get total count
        total = await self.get_count(filters=filters)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
        }


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("BaseRepository module loaded successfully")
    print("\nAvailable methods:")
    methods = [
        "get_by_id", "get_by_id_or_fail", "get_all", "get_count",
        "create", "create_batch", "update", "update_batch",
        "delete", "delete_batch", "exists", "get_by_field",
        "get_by_multiple_fields", "search", "get_all_active", "get_page"
    ]
    for method in methods:
        print(f"  - {method}()")