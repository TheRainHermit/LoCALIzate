"""
Repositories module for LoCALIzate / CaliGuia Backend
======================================================

Data access layer that encapsulates all database operations.
Provides CRUD operations and complex queries for each entity.

Available Repositories:
    - BaseRepository: Abstract base class with common CRUD operations
    - LugarRepository: Tourist places data access
    - EventoRepository: Events and festivals data access
    - UsuarioRepository: User profiles and preferences data access
    - RutaRepository: User routes and itineraries data access
    - ChatRepository: Conversations and messages data access

Usage:
    from app.repositories import LugarRepository, EventoRepository
    
    # Initialize repository (usually via dependency injection)
    lugar_repo = LugarRepository(supabase_client)
    lugares = await lugar_repo.get_all(filters={"interes": "cultura"})
"""

from app.repositories.base_repo import BaseRepository
from app.repositories.lugar_repo import LugarRepository
from app.repositories.evento_repo import EventoRepository
from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.ruta_repo import RutaRepository
from app.repositories.chat_repo import ChatRepository

__all__ = [
    # Base
    "BaseRepository",
    
    # Repositories
    "LugarRepository",
    "EventoRepository", 
    "UsuarioRepository",
    "RutaRepository",
    "ChatRepository",
]

__version__ = "1.0.0"

# Module metadata
REPOSITORY_DESCRIPTIONS = {
    "LugarRepository": "Operaciones CRUD para lugares turísticos de Cali",
    "EventoRepository": "Operaciones CRUD para eventos y festivales",
    "UsuarioRepository": "Operaciones CRUD para perfiles de usuario",
    "RutaRepository": "Operaciones CRUD para rutas e itinerarios",
    "ChatRepository": "Operaciones para conversaciones y mensajes del asistente"
}


def get_repository_names() -> list:
    """Return list of all available repository names."""
    return [
        "LugarRepository",
        "EventoRepository",
        "UsuarioRepository", 
        "RutaRepository",
        "ChatRepository"
    ]


def get_repository_description(repo_name: str) -> str:
    """Get description for a specific repository."""
    return REPOSITORY_DESCRIPTIONS.get(repo_name, "Repositorio no encontrado")


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("Repositories module loaded successfully")
    print(f"Available repositories: {', '.join(get_repository_names())}")
    print("\nRepository descriptions:")
    for repo in get_repository_names():
        print(f"  - {repo}: {get_repository_description(repo)}")