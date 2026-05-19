"""
Tests para servicios del backend.
"""

import pytest


class TestOptimizadorRutas:
    """Validar servicio de optimización de rutas."""
    
    def test_calcular_distancia_haversine(self):
        """Verificar cálculo de distancia Haversine."""
        from services.optimizador_rutas import calcular_distancia_haversine
        
        # Cristo Rey a El Gato del Río
        distancia = calcular_distancia_haversine(
            3.43587, -76.56490,  # Cristo Rey
            3.45156, -76.54297   # El Gato del Río
        )
        
        assert distancia > 0
        assert distancia < 10  # Menos de 10 km
    
    def test_calcular_tiempo_estimado(self):
        """Verificar cálculo de tiempo estimado."""
        from services.optimizador_rutas import calcular_tiempo_estimado
        
        # 2 km caminando
        tiempo = calcular_tiempo_estimado(2.0, "walking")
        assert tiempo > 0
        assert tiempo <= 30  # ~24 minutos
    
    def test_optimizar_ruta(self):
        """Verificar optimización de ruta."""
        from services.optimizador_rutas import optimizar_ruta
        
        lugares = [
            {"id": 1, "nombre": "Lugar A", "lat": 3.4516, "lng": -76.5320},
            {"id": 2, "nombre": "Lugar B", "lat": 3.4359, "lng": -76.5649},
            {"id": 3, "nombre": "Lugar C", "lat": 3.4483, "lng": -76.5319}
        ]
        
        origen_lat = 3.4516
        origen_lng = -76.5320
        
        ruta = optimizar_ruta(lugares, origen_lat, origen_lng)
        
        assert len(ruta) == len(lugares)
        assert isinstance(ruta, list)


class TestAsistenteIA:
    """Validar servicio de asistente IA."""
    
    def test_detectar_intencion(self):
        """Verificar detección de intenciones."""
        from services.asistente_ia import asistente
        
        intencion = asistente._detectar_intencion("¿Dónde puedo bailar salsa?")
        assert intencion == "salsa"
        
        intencion = asistente._detectar_intencion("Recomiéndame un restaurante")
        assert intencion == "comida"
        
        intencion = asistente._detectar_intencion("Quiero ir al río Pance")
        assert intencion == "naturaleza"
    
    def test_procesar_mensaje(self):
        """Verificar procesamiento de mensajes."""
        from services.asistente_ia import asistente
        
        resultado = asistente.procesar_mensaje("¿Dónde puedo bailar salsa en Cali?")
        
        assert "respuesta" in resultado
        assert "sugerencias" in resultado
        assert len(resultado["respuesta"]) > 0
    
    def test_generar_sugerencias(self):
        """Verificar generación de sugerencias."""
        from services.asistente_ia import asistente
        
        sugerencias = asistente._generar_sugerencias("comida")
        assert isinstance(sugerencias, list)
        assert len(sugerencias) > 0


class TestARService:
    """Validar servicio de Realidad Aumentada."""
    
    def test_calcular_distancia(self):
        """Verificar cálculo de distancia en AR."""
        from services.ar_service import ar_service
        
        distancia = ar_service.calcular_distancia_haversine(
            3.4516, -76.5320,
            3.43587, -76.56490
        )
        
        assert distancia > 0
        assert distancia < 5
    
    def test_calcular_azimuth(self):
        """Verificar cálculo de azimuth."""
        from services.ar_service import ar_service
        
        azimuth = ar_service.calcular_azimuth(
            3.4516, -76.5320,
            3.43587, -76.56490
        )
        
        assert 0 <= azimuth <= 360
    
    def test_lugares_cerca_para_ar(self):
        """Verificar obtención de lugares para AR."""
        from services.ar_service import ar_service
        
        lugares_db = [
            {"id": 1, "nombre": "Test", "lat": 3.43587, "lng": -76.56490}
        ]
        
        lugares = ar_service.lugares_cerca_para_ar(
            3.4516, -76.5320, lugares_db, heading=90
        )
        
        assert isinstance(lugares, list)


class TestGeocodingOSM:
    """Validar servicio de geocodificación OSM."""
    
    @pytest.mark.asyncio
    async def test_geocode(self):
        """Verificar geocodificación de dirección."""
        from services.geocoding_osm import geocoding_osm
        
        coords = await geocoding_osm.geocode("Cristo Rey, Cali")
        
        # Puede ser None si no hay conexión o límite de rate
        if coords:
            assert len(coords) == 2
            assert -90 <= coords[0] <= 90
            assert -180 <= coords[1] <= 180