"""
Pytest configuration and shared fixtures for CaliGuia Backend.
"""

import os
import sys
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# =====================================================
# CONFIGURACIÓN INICIAL - FORZAR CARGA DE .env
# =====================================================

# Obtener la ruta al directorio raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, '.env')

# Cargar variables de entorno de forma explícita y forzada
if os.path.exists(ENV_PATH):
    print(f"✅ Cargando archivo .env desde: {ENV_PATH}")
    load_dotenv(ENV_PATH, override=True)
else:
    print(f"❌ ADVERTENCIA: No se encontró archivo .env en: {ENV_PATH}")

# Verificar que las variables críticas se cargaron (para depuración)
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")

print(f"   SUPABASE_URL: {'✅ CARGADA' if supabase_url else '❌ NO CARGADA'}")
print(f"   SUPABASE_KEY: {'✅ CARGADA' if supabase_key else '❌ NO CARGADA'}")
print(f"   SUPABASE_SERVICE_KEY: {'✅ CARGADA' if supabase_service_key else '❌ NO CARGADA'}")

# =====================================================
# CONFIGURAR PYTHONPATH
# =====================================================

# Agregar directorio raíz al path para imports correctos
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
    print(f"✅ Directorio raíz agregado al path: {BASE_DIR}")

# =====================================================
# IMPORTAR LA APLICACIÓN
# =====================================================

try:
    from main import app
    from app.database.supabase_client import supabase_client
    print("✅ Aplicación importada correctamente")
except Exception as e:
    print(f"❌ Error importando aplicación: {str(e)}")
    raise

# =====================================================
# FIXTURES
# =====================================================


@pytest.fixture(scope="session")
def test_client():
    """
    Fixture para cliente de pruebas FastAPI.
    
    Usage:
        def test_something(test_client):
            response = test_client.get("/health")
            assert response.status_code == 200
    """
    return TestClient(app)


@pytest.fixture(scope="session")
def db_client():
    """
    Fixture para cliente de Supabase.
    
    Usage:
        def test_database(db_client):
            result = db_client.get_lugares()
            assert result is not None
    """
    return supabase_client


@pytest.fixture(scope="session")
def sample_lugar():
    """
    Fixture con datos de ejemplo de lugar turístico.
    
    Returns:
        Dict con datos de un lugar de prueba
    """
    return {
        "nombre": "Test Lugar",
        "descripcion": "Lugar de prueba para tests",
        "descripcion_corta": "Test",
        "latitud": 3.4516,
        "longitud": -76.5320,
        "direccion": "Calle Test #123",
        "barrio": "Test Barrio",
        "interes": "cultura",
        "horario": "9:00 AM - 6:00 PM",
        "precio": "Gratis",
        "icono": "📍",
        "destacado": False,
        "verificado": False
    }


@pytest.fixture(scope="session")
def sample_evento():
    """
    Fixture con datos de ejemplo de evento.
    
    Returns:
        Dict con datos de un evento de prueba
    """
    from datetime import date
    
    return {
        "nombre": "Test Evento",
        "descripcion": "Evento de prueba para tests",
        "descripcion_corta": "Evento Test",
        "fecha_inicio": date(2026, 12, 25),
        "fecha_fin": date(2026, 12, 30),
        "ubicacion": "Test Location",
        "direccion": "Calle Test #456",
        "destacado": True,
        "precio": "Gratis",
        "icono": "🎉",
        "tags": ["test", "evento"]
    }


@pytest.fixture(scope="session")
def sample_usuario():
    """
    Fixture con datos de ejemplo de usuario.
    
    Returns:
        Dict con datos de un usuario de prueba
    """
    return {
        "email": "test@example.com",
        "nombre": "Test User",
        "apellido": "Test Lastname",
        "ciudad": "Cali",
        "pais": "Colombia",
        "edad": 25,
        "intereses": ["cultura", "gastronomia"]
    }


@pytest.fixture(scope="session")
def sample_ruta():
    """
    Fixture con datos de ejemplo de ruta.
    
    Returns:
        Dict con datos de una ruta de prueba
    """
    return {
        "nombre": "Test Ruta",
        "descripcion": "Ruta de prueba para tests",
        "lugares_ids": [1, 2, 3],
        "origen_lat": 3.4516,
        "origen_lng": -76.5320
    }


@pytest.fixture
def auth_headers():
    """
    Fixture para headers de autenticación (para pruebas con auth).
    
    Returns:
        Dict con headers de autorización
    """
    # En desarrollo, se puede usar un token de prueba
    # En producción, obtener token real
    return {
        "Authorization": "Bearer test-token-123"
    }


@pytest.fixture
def cleanup_database():
    """
    Fixture para limpiar datos de prueba después de cada test.
    
    Usage:
        def test_create_item(cleanup_database):
            # Crear item de prueba
            yield
            # Limpiar después del test
    """
    # Setup: preparar datos si es necesario
    yield
    # Teardown: limpiar datos de prueba
    # (implementar según necesidades)
    pass


# =====================================================
# CONFIGURACIÓN DE PYTEST
# =====================================================

def pytest_configure(config):
    """
    Hook que se ejecuta al iniciar pytest.
    Permite configurar marcadores personalizados.
    """
    # Registrar marcadores personalizados
    config.addinivalue_line(
        "markers", 
        "slow: marca tests que son lentos"
    )
    config.addinivalue_line(
        "markers",
        "integration: marca tests de integración"
    )
    config.addinivalue_line(
        "markers",
        "skip_ci: marca tests que saltan en CI"
    )


def pytest_collection_modifyitems(config, items):
    """
    Hook para modificar la colección de tests.
    Útil para agregar marcadores automáticos.
    """
    for item in items:
        # Agregar marcador 'integration' a tests en test_integration.py
        if "test_integration" in str(item.parent):
            item.add_marker(pytest.mark.integration)


# =====================================================
# INFO
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Pytest Configuration - Conftest")
    print("=" * 50)
    print("\n✅ Fixtures disponibles:")
    print("   - test_client: Cliente FastAPI para pruebas")
    print("   - db_client: Cliente de Supabase")
    print("   - sample_lugar: Datos de lugar de ejemplo")
    print("   - sample_evento: Datos de evento de ejemplo")
    print("   - sample_usuario: Datos de usuario de ejemplo")
    print("   - sample_ruta: Datos de ruta de ejemplo")
    print("   - auth_headers: Headers de autenticación")
    print("   - cleanup_database: Limpieza de datos de prueba")
    
    print("\n📝 Marcadores registrados:")
    print("   - @pytest.mark.slow: Tests lentos")
    print("   - @pytest.mark.integration: Tests de integración")
    print("   - @pytest.mark.skip_ci: Tests que saltan en CI")
    
    print("\n✅ Conftest cargado correctamente")