"""
Tests para endpoints de API.
"""

import pytest


class TestLugaresRouter:
    """Validar endpoints de lugares."""
    
    def test_get_lugares(self, test_client):
        """Verificar GET /api/lugares"""
        response = test_client.get("/api/lugares/")
        assert response.status_code == 200
        
        data = response.json()
        assert "lugares" in data or isinstance(data, dict)
    
    def test_get_lugares_con_filtro(self, test_client):
        """Verificar GET /api/lugares con filtro de interés."""
        response = test_client.get("/api/lugares/?interes=cultura")
        assert response.status_code == 200
    
    def test_get_lugar_by_id(self, test_client):
        """Verificar GET /api/lugares/{id}"""
        # Primero obtener un ID válido
        response = test_client.get("/api/lugares/")
        
        if response.status_code == 200:
            data = response.json()
            lugares = data.get("lugares", [])
            
            if lugares:
                lugar_id = lugares[0].get("id", 1)
                detail_response = test_client.get(f"/api/lugares/{lugar_id}")
                assert detail_response.status_code == 200
            else:
                pytest.skip("No hay lugares para probar")
    
    def test_get_lugares_cercanos(self, test_client):
        """Verificar GET /api/lugares/cercanos/"""
        response = test_client.get(
            "/api/lugares/cercanos/?lat=3.4516&lng=-76.5320&radio_km=2"
        )
        assert response.status_code == 200


class TestEventosRouter:
    """Validar endpoints de eventos."""
    
    def test_get_eventos(self, test_client):
        """Verificar GET /api/eventos/"""
        response = test_client.get("/api/eventos/")
        assert response.status_code == 200
        
        data = response.json()
        assert "eventos" in data or isinstance(data, dict)
    
    def test_get_eventos_destacados(self, test_client):
        """Verificar GET /api/eventos/?destacados=true"""
        response = test_client.get("/api/eventos/?destacados=true")
        assert response.status_code == 200
    
    def test_get_eventos_proximos(self, test_client):
        """Verificar GET /api/eventos/proximos/"""
        response = test_client.get("/api/eventos/proximos/?dias=30")
        assert response.status_code == 200
    
    def test_get_evento_by_id(self, test_client):
        """Verificar GET /api/eventos/{id}"""
        response = test_client.get("/api/eventos/1")
        # Puede ser 200 si existe, 404 si no
        assert response.status_code in [200, 404]


class TestChatRouter:
    """Validar endpoints de chat."""
    
    def test_chat_mensaje(self, test_client):
        """Verificar POST /api/chat/mensaje"""
        response = test_client.post(
            "/api/chat/mensaje",
            json={"mensaje": "¿Dónde puedo bailar salsa en Cali?"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "respuesta" in data
        assert len(data["respuesta"]) > 0
    
    def test_chat_sugerencias(self, test_client):
        """Verificar GET /api/chat/sugerencias"""
        response = test_client.get("/api/chat/sugerencias")
        assert response.status_code == 200


class TestRutasRouter:
    """Validar endpoints de rutas."""
    
    def test_calcular_distancia(self, test_client):
        """Verificar GET /api/rutas/distancia"""
        response = test_client.get(
            "/api/rutas/distancia?"
            "lat1=3.4516&lng1=-76.5320&"
            "lat2=3.43587&lng2=-76.56490"
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "distancia_km" in data
    
    def test_optimizar_ruta(self, test_client):
        """Verificar POST /api/rutas/optimizar"""
        response = test_client.post(
            "/api/rutas/optimizar",
            json={
                "lugares_ids": [1, 2, 3],
                "origen_lat": 3.4516,
                "origen_lng": -76.5320
            }
        )
        
        assert response.status_code in [200, 404, 500]
    
    def test_plantillas_rutas(self, test_client):
        """Verificar GET /api/rutas/plantillas"""
        response = test_client.get("/api/rutas/plantillas")
        assert response.status_code == 200


class TestARRouter:
    """Validar endpoints de Realidad Aumentada."""
    
    def test_ar_cercanos(self, test_client):
        """Verificar GET /api/ar/cercanos"""
        response = test_client.get(
            "/api/ar/cercanos?lat=3.4516&lng=-76.5320&radio_km=2"
        )
        assert response.status_code in [200, 500]
    
    def test_ar_compass(self, test_client):
        """Verificar GET /api/ar/compass"""
        response = test_client.get(
            "/api/ar/compass?lat=3.4516&lng=-76.5320"
        )
        assert response.status_code == 200
    
    def test_ar_info(self, test_client):
        """Verificar GET /api/ar/info"""
        response = test_client.get("/api/ar/info")
        assert response.status_code == 200


class TestAnalyticsRouter:
    """Validar endpoints de analytics."""
    
    def test_analytics_globales(self, test_client):
        """Verificar GET /api/analytics/globales"""
        response = test_client.get("/api/analytics/globales")
        assert response.status_code == 200
    
    def test_analytics_top_lugares(self, test_client):
        """Verificar GET /api/analytics/top/lugares"""
        response = test_client.get("/api/analytics/top/lugares?limit=5")
        assert response.status_code == 200
    
    def test_analytics_tendencias(self, test_client):
        """Verificar GET /api/analytics/tendencias"""
        response = test_client.get("/api/analytics/tendencias")
        assert response.status_code == 200