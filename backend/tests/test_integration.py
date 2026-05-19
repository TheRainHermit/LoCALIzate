"""
Tests de integración - Flujos completos.
"""

import pytest


class TestUserJourney:
    """Flujo completo de usuario."""
    
    def test_full_user_experience(self, test_client):
        """Simular experiencia completa de usuario."""
        
        # 1. Verificar health
        health = test_client.get("/health")
        assert health.status_code == 200
        
        # 2. Ver lugares
        lugares = test_client.get("/api/lugares/")
        assert lugares.status_code == 200
        
        # 3. Ver eventos
        eventos = test_client.get("/api/eventos/")
        assert eventos.status_code == 200
        
        # 4. Buscar lugares cercanos
        cercanos = test_client.get("/api/lugares/cercanos/?lat=3.4516&lng=-76.5320")
        assert cercanos.status_code == 200
        
        # 5. Chat con asistente
        chat = test_client.post(
            "/api/chat/mensaje",
            json={"mensaje": "Recomiéndame un lugar para comer"}
        )
        assert chat.status_code == 200
        assert "respuesta" in chat.json()
        
        # 6. Calcular ruta
        ruta = test_client.post(
            "/api/rutas/optimizar",
            json={
                "lugares_ids": [1, 2, 3],
                "origen_lat": 3.4516,
                "origen_lng": -76.5320
            }
        )
        assert ruta.status_code in [200, 404]
    
    def test_ar_experience(self, test_client):
        """Simular experiencia de Realidad Aumentada."""
        
        # 1. Obtener lugares cercanos
        cercanos = test_client.get("/api/ar/cercanos?lat=3.4516&lng=-76.5320")
        
        # 2. Obtener brújula
        compass = test_client.get("/api/ar/compass?lat=3.4516&lng=-76.5320")
        assert compass.status_code == 200
        
        # 3. Ver info del servicio
        info = test_client.get("/api/ar/info")
        assert info.status_code == 200


class TestSearchFlows:
    """Flujos de búsqueda."""
    
    def test_search_by_interest(self, test_client):
        """Búsqueda por interés."""
        intereses = ["cultura", "naturaleza", "gastronomia", "salsa"]
        
        for interes in intereses:
            response = test_client.get(f"/api/lugares/?interes={interes}")
            assert response.status_code == 200
    
    def test_search_by_location(self, test_client):
        """Búsqueda por ubicación."""
        # Centro de Cali
        response = test_client.get("/api/lugares/cercanos/?lat=3.4516&lng=-76.5320")
        assert response.status_code == 200
        
        # Cristo Rey
        response = test_client.get("/api/lugares/cercanos/?lat=3.43587&lng=-76.56490")
        assert response.status_code == 200
    
    def test_search_by_text(self, test_client):
        """Búsqueda por texto."""
        # No hay endpoint de búsqueda directo, pero se puede probar filtros
        response = test_client.get("/api/lugares/")
        assert response.status_code == 200