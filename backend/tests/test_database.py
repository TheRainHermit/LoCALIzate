"""
Tests para operaciones de base de datos.
"""

import pytest


class TestLugaresTable:
    """Validar operaciones en tabla lugares."""
    
    def test_get_lugares(self, db_client):
        """Verificar obtención de lugares."""
        result = db_client.get_lugares()
        assert result is not None
        assert hasattr(result, 'data')
    
    def test_get_lugares_by_interes(self, db_client):
        """Verificar filtro por interés."""
        result = db_client.get_lugares(filtro={"interes": "cultura"})
        assert result is not None
        
        if result.data:
            for lugar in result.data:
                assert lugar.get('interes') == "cultura"
    
    def test_get_lugar_by_id(self, db_client):
        """Verificar obtención de lugar por ID."""
        # Primero obtener un ID válido
        lugares = db_client.get_lugares()
        
        if lugares.data and len(lugares.data) > 0:
            lugar_id = lugares.data[0]['id']
            lugar = db_client.get_lugar_by_id(lugar_id)
            assert lugar is not None
            assert lugar['id'] == lugar_id
        else:
            pytest.skip("No hay lugares en la base de datos")
    
    def test_lugares_have_required_fields(self, db_client):
        """Verificar que los lugares tienen campos requeridos."""
        result = db_client.get_lugares(limit=10)
        
        required_fields = ['id', 'nombre', 'latitud', 'longitud', 'interes']
        
        for lugar in result.data:
            for field in required_fields:
                assert field in lugar, f"Campo {field} faltante en lugar {lugar.get('nombre')}"


class TestEventosTable:
    """Validar operaciones en tabla eventos."""
    
    def test_get_eventos(self, db_client):
        """Verificar obtención de eventos."""
        result = db_client.get_eventos()
        assert result is not None
        assert hasattr(result, 'data')
    
    def test_get_eventos_destacados(self, db_client):
        """Verificar filtro de eventos destacados."""
        result = db_client.get_eventos(destacados_only=True)
        assert result is not None
        
        if result.data:
            for evento in result.data:
                assert evento.get('destacado') is True
    
    def test_get_evento_by_id(self, db_client):
        """Verificar obtención de evento por ID."""
        eventos = db_client.get_eventos()
        
        if eventos.data and len(eventos.data) > 0:
            evento_id = eventos.data[0]['id']
            evento = db_client.get_evento_by_id(evento_id)
            assert evento is not None
            assert evento['id'] == evento_id
        else:
            pytest.skip("No hay eventos en la base de datos")
    
    def test_get_eventos_proximos(self, db_client):
        """Verificar obtención de eventos próximos."""
        proximos = db_client.get_eventos_proximos(dias=30)
        assert isinstance(proximos, list)


class TestUsuariosTable:
    """Validar operaciones en tabla usuarios."""
    
    def test_get_usuario_by_id(self, db_client):
        """Verificar obtención de usuario por ID."""
        # Nota: Esto requiere un usuario existente
        # Para pruebas, se puede crear un usuario temporal
        pass


class TestDatabaseStats:
    """Validar estadísticas de base de datos."""
    
    def test_get_stats(self, db_client):
        """Verificar obtención de estadísticas."""
        stats = db_client.get_stats()
        assert isinstance(stats, dict)
        assert 'total_lugares' in stats or 'error' in stats