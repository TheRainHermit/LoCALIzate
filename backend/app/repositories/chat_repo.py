"""
Chat Repository for LoCALIzate Backend
=====================================

Repository for chat conversations and messages.
Provides specialized queries for chat including:
    - Conversation management (create, get, update, delete)
    - Message management (add, get, delete)
    - Conversation history for users
    - Search messages by content
    - Get conversation statistics

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


class ChatRepository(BaseRepository):
    """
    Repository for chat conversations and messages.
    
    Attributes:
        supabase: Supabase client instance
        conversaciones_table: "conversaciones" table
        mensajes_table: "mensajes" table
    """
    
    def __init__(self, supabase: Client):
        """Initialize repository with chat tables."""
        super().__init__(supabase, "conversaciones")
        self.conversaciones_table = supabase.table("conversaciones")
        self.mensajes_table = supabase.table("mensajes")
    
    # =====================================================
    # CONVERSATION CRUD OPERATIONS
    # =====================================================
    
    async def create_conversacion(
        self,
        usuario_id: str,
        titulo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation.
        
        Args:
            usuario_id: User ID
            titulo: Conversation title (optional, auto-generated from first message)
        
        Returns:
            Created conversation
        """
        try:
            if not titulo:
                titulo = f"Conversación {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            data = {
                "usuario_id": usuario_id,
                "titulo": titulo,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.conversaciones_table.insert(data).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Created conversation for user {usuario_id}")
                return result.data[0]
            
            raise DatabaseException(
                detail="No se pudo crear la conversación",
                operation="create_conversacion",
                table="conversaciones"
            )
            
        except Exception as e:
            self._handle_error(e, "create_conversacion", usuario_id=usuario_id)
            raise
    
    async def get_conversacion(
        self,
        conversacion_id: int,
        usuario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a conversation by ID.
        
        Args:
            conversacion_id: Conversation ID
            usuario_id: Optional user ID to verify ownership
        
        Returns:
            Conversation data
        
        Raises:
            NotFoundException: If conversation not found
            DatabaseException: If user doesn't own the conversation
        """
        try:
            result = self.conversaciones_table\
                .select("*")\
                .eq("id", conversacion_id)\
                .execute()
            
            if not result.data or len(result.data) == 0:
                raise NotFoundException(
                    resource_type="Conversación",
                    resource_id=conversacion_id
                )
            
            conversation = result.data[0]
            
            # Verify ownership if usuario_id provided
            if usuario_id and conversation.get("usuario_id") != usuario_id:
                raise DatabaseException(
                    detail="No tienes permiso para ver esta conversación",
                    operation="get_conversacion",
                    table="conversaciones"
                )
            
            return conversation
            
        except NotFoundException:
            raise
        except Exception as e:
            self._handle_error(e, "get_conversacion", conversacion_id=conversacion_id)
            raise
    
    async def get_user_conversaciones(
        self,
        usuario_id: str,
        limit: int = 20,
        offset: int = 0,
        include_message_count: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user.
        
        Args:
            usuario_id: User ID
            limit: Maximum number of records
            offset: Number of records to skip
            include_message_count: If True, include message count for each conversation
        
        Returns:
            List of user conversations
        """
        try:
            result = self.conversaciones_table\
                .select("*")\
                .eq("usuario_id", usuario_id)\
                .order("updated_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            conversations = result.data if result.data else []
            
            if include_message_count and conversations:
                for conv in conversations:
                    # Get message count
                    msg_result = self.mensajes_table\
                        .select("id", count="exact")\
                        .eq("conversacion_id", conv["id"])\
                        .execute()
                    conv["mensaje_count"] = getattr(msg_result, 'count', 0) or 0
                    
                    # Get last message preview
                    last_msg = self.mensajes_table\
                        .select("contenido, rol, created_at")\
                        .eq("conversacion_id", conv["id"])\
                        .order("created_at", desc=True)\
                        .limit(1)\
                        .execute()
                    
                    if last_msg.data and len(last_msg.data) > 0:
                        conv["ultimo_mensaje"] = last_msg.data[0]["contenido"][:100]
                        conv["ultimo_mensaje_fecha"] = last_msg.data[0]["created_at"]
                        conv["ultimo_rol"] = last_msg.data[0]["rol"]
            
            return conversations
            
        except Exception as e:
            self._handle_error(e, "get_user_conversaciones", usuario_id=usuario_id)
            return []
    
    async def update_conversacion_titulo(
        self,
        conversacion_id: int,
        usuario_id: str,
        titulo: str
    ) -> Dict[str, Any]:
        """
        Update conversation title.
        
        Args:
            conversacion_id: Conversation ID
            usuario_id: User ID (for ownership check)
            titulo: New title
        
        Returns:
            Updated conversation
        """
        # Verify ownership
        conv = await self.get_conversacion(conversacion_id, usuario_id)
        
        data = {
            "titulo": titulo,
            "updated_at": datetime.now().isoformat()
        }
        
        result = self.conversaciones_table\
            .update(data)\
            .eq("id", conversacion_id)\
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        raise DatabaseException(
            detail="No se pudo actualizar el título",
            operation="update_conversacion_titulo",
            table="conversaciones"
        )
    
    async def delete_conversacion(
        self,
        conversacion_id: int,
        usuario_id: str,
        delete_messages: bool = True
    ) -> bool:
        """
        Delete a conversation and optionally its messages.
        
        Args:
            conversacion_id: Conversation ID
            usuario_id: User ID (for ownership check)
            delete_messages: If True, delete all messages in the conversation
        
        Returns:
            True if deleted
        """
        # Verify ownership
        await self.get_conversacion(conversacion_id, usuario_id)
        
        try:
            # Delete messages first if requested
            if delete_messages:
                self.mensajes_table\
                    .delete()\
                    .eq("conversacion_id", conversacion_id)\
                    .execute()
            
            # Delete conversation
            result = self.conversaciones_table\
                .delete()\
                .eq("id", conversacion_id)\
                .execute()
            
            deleted = result.data and len(result.data) > 0
            
            if deleted:
                logger.info(f"Deleted conversation {conversacion_id} for user {usuario_id}")
            
            return deleted
            
        except Exception as e:
            self._handle_error(e, "delete_conversacion", conversacion_id=conversacion_id)
            return False
    
    # =====================================================
    # MESSAGE CRUD OPERATIONS
    # =====================================================
    
    async def add_mensaje(
        self,
        conversacion_id: int,
        rol: str,
        contenido: str,
        intencion: Optional[str] = None,
        lugares_referenciados: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Add a message to a conversation.
        
        Args:
            conversacion_id: Conversation ID
            rol: Message role (user, assistant, system)
            contenido: Message content
            intencion: Detected intent (optional)
            lugares_referenciados: List of place IDs mentioned (optional)
        
        Returns:
            Created message
        """
        try:
            data = {
                "conversacion_id": conversacion_id,
                "rol": rol,
                "contenido": contenido,
                "intencion": intencion,
                "lugares_referenciados": lugares_referenciados,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.mensajes_table.insert(data).execute()
            
            if result.data and len(result.data) > 0:
                # Update conversation updated_at
                self.conversaciones_table\
                    .update({"updated_at": datetime.now().isoformat()})\
                    .eq("id", conversacion_id)\
                    .execute()
                
                return result.data[0]
            
            raise DatabaseException(
                detail="No se pudo agregar el mensaje",
                operation="add_mensaje",
                table="mensajes"
            )
            
        except Exception as e:
            self._handle_error(e, "add_mensaje", conversacion_id=conversacion_id, rol=rol)
            raise
    
    async def get_conversacion_mensajes(
        self,
        conversacion_id: int,
        usuario_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all messages in a conversation.
        
        Args:
            conversacion_id: Conversation ID
            usuario_id: Optional user ID to verify ownership
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of messages in chronological order
        """
        # Verify ownership if usuario_id provided
        if usuario_id:
            await self.get_conversacion(conversacion_id, usuario_id)
        
        try:
            result = self.mensajes_table\
                .select("*")\
                .eq("conversacion_id", conversacion_id)\
                .order("created_at")\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "get_conversacion_mensajes", conversacion_id=conversacion_id)
            return []
    
    async def get_last_messages(
        self,
        conversacion_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get last N messages from a conversation.
        
        Args:
            conversacion_id: Conversation ID
            limit: Number of messages to retrieve
        
        Returns:
            List of last messages
        """
        try:
            result = self.mensajes_table\
                .select("*")\
                .eq("conversacion_id", conversacion_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            # Return in chronological order
            messages = result.data if result.data else []
            return list(reversed(messages))
            
        except Exception as e:
            self._handle_error(e, "get_last_messages", conversacion_id=conversacion_id)
            return []
    
    # =====================================================
    # CONVERSATION WITH MESSAGES
    # =====================================================
    
    async def get_conversacion_completa(
        self,
        conversacion_id: int,
        usuario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get conversation with all messages.
        
        Args:
            conversacion_id: Conversation ID
            usuario_id: Optional user ID to verify ownership
        
        Returns:
            Conversation with messages
        """
        conversation = await self.get_conversacion(conversacion_id, usuario_id)
        messages = await self.get_conversacion_mensajes(conversacion_id, usuario_id)
        
        conversation["mensajes"] = messages
        conversation["total_mensajes"] = len(messages)
        
        return conversation
    
    async def get_or_create_conversacion(
        self,
        usuario_id: str,
        conversacion_id: Optional[int] = None,
        titulo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get existing conversation or create a new one.
        
        Args:
            usuario_id: User ID
            conversacion_id: Optional existing conversation ID
            titulo: Optional title for new conversation
        
        Returns:
            Conversation
        """
        if conversacion_id:
            try:
                return await self.get_conversacion(conversacion_id, usuario_id)
            except NotFoundException:
                # If conversation doesn't exist, create new one
                pass
        
        return await self.create_conversacion(usuario_id, titulo)
    
    # =====================================================
    # SEARCH AND QUERIES
    # =====================================================
    
    async def search_messages(
        self,
        usuario_id: str,
        search_term: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search messages by content for a user.
        
        Args:
            usuario_id: User ID
            search_term: Text to search for
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of matching messages with conversation info
        """
        try:
            # First get user's conversations
            conversations = await self.get_user_conversaciones(usuario_id, limit=100)
            conv_ids = [c["id"] for c in conversations]
            
            if not conv_ids:
                return []
            
            # Search messages in those conversations
            result = self.mensajes_table\
                .select("*, conversaciones!inner(titulo)")\
                .in_("conversacion_id", conv_ids)\
                .ilike("contenido", f"%{search_term}%")\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error(e, "search_messages", usuario_id=usuario_id, search_term=search_term)
            return []
    
    async def get_conversation_stats(
        self,
        usuario_id: str
    ) -> Dict[str, Any]:
        """
        Get chat statistics for a user.
        
        Args:
            usuario_id: User ID
        
        Returns:
            Chat statistics
        """
        try:
            conversations = await self.get_user_conversaciones(usuario_id, limit=1000)
            
            total_conversations = len(conversations)
            total_messages = sum(c.get("mensaje_count", 0) for c in conversations)
            
            # Get messages by role
            user_messages = 0
            assistant_messages = 0
            
            for conv in conversations:
                msg_result = self.mensajes_table\
                    .select("rol", count="exact")\
                    .eq("conversacion_id", conv["id"])\
                    .execute()
                
                for msg in (msg_result.data or []):
                    if msg.get("rol") == "user":
                        user_messages += 1
                    elif msg.get("rol") == "assistant":
                        assistant_messages += 1
            
            # Get last activity
            last_activity = None
            if conversations:
                last_conv = conversations[0]
                last_activity = last_conv.get("updated_at")
            
            return {
                "total_conversaciones": total_conversations,
                "total_mensajes": total_messages,
                "mensajes_usuario": user_messages,
                "mensajes_asistente": assistant_messages,
                "ultima_actividad": last_activity,
                "conversaciones_activas": sum(1 for c in conversations if c.get("mensaje_count", 0) > 0)
            }
            
        except Exception as e:
            self._handle_error(e, "get_conversation_stats", usuario_id=usuario_id)
            return {}
    
    async def delete_old_conversations(
        self,
        days_old: int = 30
    ) -> int:
        """
        Delete conversations older than specified days.
        
        Args:
            days_old: Age threshold in days
        
        Returns:
            Number of deleted conversations
        """
        try:
            from datetime import timedelta
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            # Get old conversations
            old_convs = self.conversaciones_table\
                .select("id")\
                .lt("updated_at", cutoff_date)\
                .execute()
            
            conv_ids = [c["id"] for c in (old_convs.data or [])]
            
            if not conv_ids:
                return 0
            
            # Delete messages first
            self.mensajes_table\
                .delete()\
                .in_("conversacion_id", conv_ids)\
                .execute()
            
            # Delete conversations
            result = self.conversaciones_table\
                .delete()\
                .in_("id", conv_ids)\
                .execute()
            
            deleted = len(result.data) if result.data else 0
            logger.info(f"Deleted {deleted} old conversations (older than {days_old} days)")
            
            return deleted
            
        except Exception as e:
            self._handle_error(e, "delete_old_conversations", days_old=days_old)
            return 0


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("ChatRepository module loaded successfully")
    print("\nAvailable custom methods:")
    methods = [
        "create_conversacion()",
        "get_conversacion()",
        "get_user_conversaciones()",
        "update_conversacion_titulo()",
        "delete_conversacion()",
        "add_mensaje()",
        "get_conversacion_mensajes()",
        "get_last_messages()",
        "get_conversacion_completa()",
        "get_or_create_conversacion()",
        "search_messages()",
        "get_conversation_stats()",
        "delete_old_conversations()"
    ]
    for method in methods:
        print(f"  - {method}")