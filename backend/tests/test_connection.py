"""
Tests para validar conexiones básicas.
"""

import pytest
import os
from dotenv import load_dotenv

load_dotenv()


class TestEnvironment:
    """Validar variables de entorno."""
    
    def test_env_file_exists(self):
        """Verificar que archivo .env existe."""
        assert os.path.exists(".env"), "Archivo .env no encontrado"
    
    def test_supabase_url_configured(self):
        """Verificar que SUPABASE_URL está configurada."""
        url = os.getenv("SUPABASE_URL")
        assert url is not None, "SUPABASE_URL no configurada"
        assert url.startswith("https://"), "SUPABASE_URL debe comenzar con https://"
    
    def test_supabase_key_configured(self):
        """Verificar que SUPABASE_KEY está configurada."""
        key = os.getenv("SUPABASE_KEY")
        assert key is not None, "SUPABASE_KEY no configurada"
        assert len(key) > 10, "SUPABASE_KEY parece inválida"


class TestSupabaseConnection:
    """Validar conexión a Supabase."""
    
    def test_supabase_client_initialization(self, db_client):
        """Verificar que el cliente Supabase se inicializa correctamente."""
        assert db_client is not None
        assert db_client.get_client() is not None
    
    def test_supabase_connection_test(self, db_client):
        """Verificar conexión real a Supabase."""
        result = db_client.test_connection()
        assert result is True, "No se pudo conectar a Supabase"
    
    def test_supabase_query_lugares(self, db_client):
        """Verificar consulta a tabla lugares."""
        client = db_client.get_client()
        result = client.table("lugares").select("*").limit(1).execute()
        assert result is not None
        assert hasattr(result, 'data')


class TestFastAPIApp:
    """Validar aplicación FastAPI."""
    
    def test_app_created(self, test_client):
        """Verificar que la app FastAPI está creada."""
        assert test_client is not None
    
    def test_root_endpoint(self, test_client):
        """Verificar endpoint raíz."""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "name" in response.json() or "message" in response.json()
    
    def test_health_endpoint(self, test_client):
        """Verificar health check."""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] in ["healthy", "degraded"]
    
    def test_version_endpoint(self, test_client):
        """Verificar endpoint de versión."""
        response = test_client.get("/version")
        assert response.status_code == 200
        assert "version" in response.json()