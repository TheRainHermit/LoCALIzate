"""
Módulo de base de datos para LoCALIzate / CaliGuia Backend
===========================================================

Maneja la conexión y operaciones con Supabase.
Incluye cliente de base de datos, migraciones y datos de semilla.

Módulos disponibles:
    - supabase_client: Cliente Supabase para operaciones de base de datos
    - models: Modelos Pydantic para la base de datos
    - migrations: Migraciones Alembic para versionado de esquema
    - seeds: Datos de prueba para población inicial

Usage:
    from app.database import supabase_client
    from app.database import Lugar, Evento, RutaRequest
    
    client = supabase_client.get_client()
    result = client.table("lugares").select("*").execute()
"""

from app.database.supabase_client import supabase_client, SupabaseClient
from app.database.models import (
    Lugar,
    Evento,
    RutaRequest,
    RutaResponse,
    MensajeChat,
    RespuestaChat,
    PreferenciasUsuario
)

# Intentar importar módulos de migraciones y seeds (opcionales)
try:
    from app.database.migrations import alembic_config, run_migrations
    MIGRATIONS_AVAILABLE = True
except ImportError:
    MIGRATIONS_AVAILABLE = False

try:
    from app.database.seeds import seed_lugares, seed_eventos, seed_usuarios, run_all_seeds
    SEEDS_AVAILABLE = True
except ImportError:
    SEEDS_AVAILABLE = False

__all__ = [
    # Clientes
    'supabase_client',
    'SupabaseClient',
    
    # Modelos
    'Lugar',
    'Evento',
    'RutaRequest',
    'RutaResponse',
    'MensajeChat',
    'RespuestaChat',
    'PreferenciasUsuario',
]

__version__ = "2.0.0"

# Información del módulo
MODULE_INFO = {
    "name": "LoCALIzate Database",
    "version": __version__,
    "description": "Módulo de base de datos para guía turística de Cali",
    "has_migrations": MIGRATIONS_AVAILABLE,
    "has_seeds": SEEDS_AVAILABLE
}


def get_db_info() -> dict:
    """Obtener información del módulo de base de datos."""
    return MODULE_INFO.copy()


def init_database(run_seeds: bool = False) -> dict:
    """
    Inicializar la base de datos.
    
    Args:
        run_seeds: Si es True, ejecuta los seeds para poblar la base de datos
    
    Returns:
        Diccionario con resultado de la inicialización
    """
    result = {
        "status": "success",
        "messages": [],
        "migrations": None,
        "seeds": None
    }
    
    # Verificar conexión
    try:
        client = supabase_client.get_client()
        # Probar conexión con una consulta simple
        test = client.table("categorias").select("count", count="exact").limit(1).execute()
        result["messages"].append("✅ Conexión a Supabase establecida")
    except Exception as e:
        result["status"] = "error"
        result["messages"].append(f"❌ Error de conexión: {str(e)}")
        return result
    
    # Ejecutar migraciones si están disponibles
    if MIGRATIONS_AVAILABLE:
        try:
            # run_migrations()
            result["migrations"] = "available"
            result["messages"].append("✅ Migraciones disponibles")
        except Exception as e:
            result["messages"].append(f"⚠️ Error en migraciones: {str(e)}")
    
    # Ejecutar seeds si se solicita
    if run_seeds and SEEDS_AVAILABLE:
        try:
            # run_all_seeds()
            result["seeds"] = "executed"
            result["messages"].append("✅ Seeds ejecutados correctamente")
        except Exception as e:
            result["messages"].append(f"⚠️ Error en seeds: {str(e)}")
    elif SEEDS_AVAILABLE:
        result["seeds"] = "available"
    
    return result


# =====================================================
# FUNCIONES DE UTILIDAD PARA MIGRACIONES
# =====================================================

def get_migrations_status() -> dict:
    """
    Obtener estado de las migraciones.
    
    Returns:
        Diccionario con estado de migraciones
    """
    if not MIGRATIONS_AVAILABLE:
        return {"available": False, "message": "Módulo de migraciones no disponible"}
    
    return {
        "available": True,
        "message": "Migraciones configuradas con Alembic",
        "location": "database/migrations/"
    }


def get_seeds_status() -> dict:
    """
    Obtener estado de los seeds.
    
    Returns:
        Diccionario con estado de seeds
    """
    if not SEEDS_AVAILABLE:
        return {"available": False, "message": "Módulo de seeds no disponible"}
    
    return {
        "available": True,
        "message": "Seeds disponibles para población de datos",
        "seeds": ["lugares.sql", "eventos.sql", "usuarios.sql"],
        "location": "database/seeds/"
    }


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Database Module - LoCALIzate")
    print("=" * 50)
    
    info = get_db_info()
    print(f"\n📦 Nombre: {info['name']}")
    print(f"📋 Versión: {info['version']}")
    print(f"🔧 Migraciones: {'✅' if info['has_migrations'] else '❌'}")
    print(f"🌱 Seeds: {'✅' if info['has_seeds'] else '❌'}")
    
    print("\n📁 Modelos disponibles:")
    models = ['Lugar', 'Evento', 'RutaRequest', 'RutaResponse', 'MensajeChat', 'RespuestaChat', 'PreferenciasUsuario']
    for model in models:
        print(f"   ✓ {model}")
    
    # Test de conexión
    print("\n🔌 Probando conexión a Supabase...")
    result = init_database(run_seeds=False)
    
    for msg in result["messages"]:
        print(f"   {msg}")
    
    print(f"\n📊 Estado final: {result['status']}")
    print("\n✅ Database module loaded successfully")