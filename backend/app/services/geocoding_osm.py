"""
Servicio de Geocodificación con OpenStreetMap Nominatim
========================================================

Servicio completamente gratuito para conversión entre direcciones y coordenadas.
No requiere API key ni tarjeta de crédito.

Características:
    - Geocodificación: dirección → coordenadas (lat, lng)
    - Geocodificación inversa: coordenadas → dirección
    - Búsqueda de lugares cercanos
    - Límite de 1 request por segundo (respetar política de OSM)
    - Cache en memoria para evitar requests duplicados

API Reference: https://nominatim.org/release-docs/develop/api/Overview/
Política de uso: https://operations.osmfoundation.org/policies/nominatim/
"""

import httpx
import asyncio
import hashlib
import json
import logging
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime, timedelta
from functools import wraps
from collections import OrderedDict

from app.core.config import settings
from app.core.exceptions import GeocodingException, RateLimitException

# Configure logging
logger = logging.getLogger(__name__)


# =====================================================
# RATE LIMITING DECORATOR
# =====================================================

class SimpleCache:
    """Cache simple en memoria con TTL."""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def _make_key(self, *args, **kwargs) -> str:
        """Generar clave única para cache."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, *args, **kwargs) -> Optional[Any]:
        """Obtener valor del cache."""
        key = self._make_key(*args, **kwargs)
        
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl_seconds):
                # Mover al final (LRU)
                self.cache.move_to_end(key)
                return value
            else:
                # Expiró
                del self.cache[key]
        
        return None
    
    def set(self, value: Any, *args, **kwargs) -> None:
        """Guardar valor en cache."""
        key = self._make_key(*args, **kwargs)
        
        # Si ya existe, actualizar
        if key in self.cache:
            del self.cache[key]
        
        # Si excede tamaño, eliminar el más antiguo
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        self.cache[key] = (value, datetime.now())


class RateLimiter:
    """Rate limiter para respetar política de OSM (1 request/segundo)."""
    
    def __init__(self, requests_per_second: float = 1.0):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time: Optional[datetime] = None
        self._lock = asyncio.Lock()
    
    async def wait_if_needed(self):
        """Esperar si es necesario para respetar rate limit."""
        async with self._lock:
            if self.last_request_time:
                elapsed = (datetime.now() - self.last_request_time).total_seconds()
                if elapsed < self.min_interval:
                    wait_time = self.min_interval - elapsed
                    logger.debug(f"Rate limit: esperando {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
            
            self.last_request_time = datetime.now()


# =====================================================
# SERVICIO PRINCIPAL
# =====================================================

class GeocodingOSM:
    """
    Servicio gratuito de geocodificación usando OpenStreetMap Nominatim.
    
    Attributes:
        base_url: URL base de la API de Nominatim
        user_agent: Identificador de la aplicación
        rate_limiter: Limitador de requests
        cache: Cache en memoria
        timeout: Timeout para requests HTTP
    """
    
    def __init__(
        self,
        user_agent: Optional[str] = None,
        timeout: float = 10.0,
        enable_cache: bool = True
    ):
        """
        Inicializar servicio de geocodificación OSM.
        
        Args:
            user_agent: Identificador de la aplicación (requerido por OSM)
            timeout: Timeout para requests HTTP en segundos
            enable_cache: Habilitar cache en memoria
        """
        self.base_url = "https://nominatim.openstreetmap.org"
        
        # User-Agent personalizable (requerido por política de OSM)
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = settings.APP_NAME + "/1.0 (https://LoCALIzate.com)"
        
        self.timeout = timeout
        self.rate_limiter = RateLimiter(requests_per_second=1.0)
        self.cache = SimpleCache(max_size=200, ttl_seconds=7200) if enable_cache else None
        self.enable_cache = enable_cache
        
        logger.info(f"GeocodingOSM inicializado. User-Agent: {self.user_agent}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Obtener headers para requests HTTP."""
        return {
            'User-Agent': self.user_agent,
            'Accept-Language': 'es,en;q=0.9',
            'Accept': 'application/json'
        }
    
    # =====================================================
    # MÉTODOS PRINCIPALES
    # =====================================================
    
    async def geocode(
        self, 
        direccion: str,
        country: str = "Colombia",
        city: str = "Cali"
    ) -> Optional[Tuple[float, float]]:
        """
        Convertir dirección a coordenadas (lat, lng).
        
        Args:
            direccion: Dirección o nombre del lugar
            country: País para acotar búsqueda (default: Colombia)
            city: Ciudad para acotar búsqueda (default: Cali)
        
        Returns:
            Tupla (latitud, longitud) o None si no se encuentra
        
        Raises:
            GeocodingException: Error en la geocodificación
            RateLimitException: Rate limit excedido
        """
        # Verificar cache
        if self.enable_cache and self.cache:
            cached = self.cache.get(direccion, country=country, city=city)
            if cached:
                logger.debug(f"Cache hit para: {direccion}")
                return cached
        
        # Mejorar la dirección para búsqueda más precisa
        search_query = f"{direccion}, {city}, {country}"
        
        async with httpx.AsyncClient() as client:
            try:
                # Aplicar rate limiting
                await self.rate_limiter.wait_if_needed()
                
                params = {
                    'q': search_query,
                    'format': 'json',
                    'limit': 1,
                    'addressdetails': 0,
                    'countrycodes': 'co',
                    'dedupe': 1
                }
                
                logger.debug(f"Geocoding: {search_query}")
                
                response = await client.get(
                    f"{self.base_url}/search",
                    params=params,
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        lat = float(data[0]['lat'])
                        lon = float(data[0]['lon'])
                        result = (lat, lon)
                        
                        # Guardar en cache
                        if self.enable_cache and self.cache:
                            self.cache.set(result, direccion, country=country, city=city)
                        
                        logger.info(f"Geocode exitoso: '{direccion}' -> ({lat:.6f}, {lon:.6f})")
                        return result
                    else:
                        logger.warning(f"No se encontró: {direccion}")
                        return None
                elif response.status_code == 429:
                    raise RateLimitException(
                        detail="Límite de requests de geocodificación excedido",
                        retry_after=60
                    )
                else:
                    raise GeocodingException(
                        address=direccion,
                        detail=f"Error HTTP {response.status_code}",
                        original_error=response.text[:200]
                    )
                    
            except httpx.TimeoutException:
                logger.error(f"Timeout geocoding: {direccion}")
                raise GeocodingException(
                    address=direccion,
                    detail="Timeout en la solicitud",
                    original_error="Request timeout"
                )
            except Exception as e:
                logger.error(f"Error en geocoding: {str(e)}")
                raise GeocodingException(
                    address=direccion,
                    detail="Error en servicio de geocodificación",
                    original_error=str(e)
                )
    
    async def reverse_geocode(
        self, 
        lat: float, 
        lng: float,
        zoom: int = 18
    ) -> Optional[str]:
        """
        Convertir coordenadas a dirección.
        
        Args:
            lat: Latitud
            lng: Longitud
            zoom: Nivel de detalle (1-18, mayor = más detalle)
        
        Returns:
            Dirección formateada o None si no se encuentra
        
        Raises:
            GeocodingException: Error en la geocodificación inversa
        """
        cache_key = f"reverse_{lat}_{lng}_{zoom}"
        
        # Verificar cache
        if self.enable_cache and self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit para reverse: ({lat}, {lng})")
                return cached
        
        async with httpx.AsyncClient() as client:
            try:
                await self.rate_limiter.wait_if_needed()
                
                params = {
                    'lat': lat,
                    'lon': lng,
                    'format': 'json',
                    'zoom': zoom,
                    'addressdetails': 1
                }
                
                logger.debug(f"Reverse geocoding: ({lat}, {lng})")
                
                response = await client.get(
                    f"{self.base_url}/reverse",
                    params=params,
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and 'display_name' in data:
                        direccion = data['display_name']
                        
                        # Guardar en cache
                        if self.enable_cache and self.cache:
                            self.cache.set(direccion, cache_key)
                        
                        logger.info(f"Reverse geocode exitoso: ({lat:.6f}, {lng:.6f}) -> '{direccion[:50]}...'")
                        return direccion
                    else:
                        logger.warning(f"No se encontró dirección para: ({lat}, {lng})")
                        return None
                elif response.status_code == 429:
                    raise RateLimitException(
                        detail="Límite de requests de geocodificación excedido",
                        retry_after=60
                    )
                else:
                    raise GeocodingException(
                        address=f"({lat}, {lng})",
                        detail=f"Error HTTP {response.status_code}",
                        original_error=response.text[:200]
                    )
                    
            except Exception as e:
                logger.error(f"Error en reverse geocoding: {str(e)}")
                raise GeocodingException(
                    address=f"({lat}, {lng})",
                    detail="Error en servicio de geocodificación inversa",
                    original_error=str(e)
                )
    
    async def buscar_lugares_cerca(
        self, 
        lat: float, 
        lng: float, 
        radio_metros: int = 1000,
        tipo: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Buscar lugares cerca de una ubicación.
        
        Args:
            lat: Latitud de referencia
            lng: Longitud de referencia
            radio_metros: Radio de búsqueda en metros
            tipo: Tipo de lugar (restaurant, museum, park, etc.)
            limit: Máximo número de resultados
        
        Returns:
            Lista de lugares cercanos con nombre, coordenadas y distancia
        
        Raises:
            GeocodingException: Error en la búsqueda
        """
        cache_key = f"nearby_{lat}_{lng}_{radio_metros}_{tipo}_{limit}"
        
        # Verificar cache
        if self.enable_cache and self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit para nearby: ({lat}, {lng})")
                return cached
        
        async with httpx.AsyncClient() as client:
            try:
                await self.rate_limiter.wait_if_needed()
                
                params = {
                    'lat': lat,
                    'lon': lng,
                    'radius': radio_metros,
                    'format': 'json',
                    'limit': limit,
                    'extratags': 1
                }
                
                if tipo:
                    # Mapear tipos comunes de OSM
                    tipo_map = {
                        'restaurant': 'amenity=restaurant',
                        'cafe': 'amenity=cafe',
                        'park': 'leisure=park',
                        'museum': 'tourism=museum',
                        'hotel': 'tourism=hotel',
                        'church': 'building=church'
                    }
                    params['featuretype'] = tipo_map.get(tipo, tipo)
                
                logger.debug(f"Buscando lugares cerca de ({lat}, {lng}) en {radio_metros}m")
                
                response = await client.get(
                    f"{self.base_url}/search",
                    params=params,
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    for item in data:
                        lugar_lat = float(item.get('lat', 0))
                        lugar_lon = float(item.get('lon', 0))
                        
                        # Calcular distancia si tenemos coordenadas
                        distancia = None
                        if lugar_lat and lugar_lon:
                            from app.services.optimizador_rutas import calcular_distancia_haversine
                            distancia = calcular_distancia_haversine(lat, lng, lugar_lat, lugar_lon)
                        
                        results.append({
                            'nombre': item.get('display_name', '').split(',')[0],
                            'direccion': item.get('display_name'),
                            'lat': lugar_lat,
                            'lng': lugar_lon,
                            'distancia_km': round(distancia, 2) if distancia else None,
                            'tipo': item.get('type'),
                            'icono': item.get('icon', '📍')
                        })
                    
                    # Guardar en cache
                    if self.enable_cache and self.cache:
                        self.cache.set(results, cache_key)
                    
                    logger.info(f"Encontrados {len(results)} lugares cerca de ({lat}, {lng})")
                    return results
                    
                else:
                    raise GeocodingException(
                        address=f"({lat}, {lng})",
                        detail=f"Error HTTP {response.status_code}",
                        original_error=response.text[:200]
                    )
                    
            except Exception as e:
                logger.error(f"Error buscando lugares cercanos: {str(e)}")
                raise GeocodingException(
                    address=f"({lat}, {lng})",
                    detail="Error en búsqueda de lugares cercanos",
                    original_error=str(e)
                )
    
    async def buscar_pois_cali(
        self,
        lat: float,
        lng: float,
        interes: Optional[str] = None,
        radio_metros: int = 5000
    ) -> List[Dict[str, Any]]:
        """
        Buscar puntos de interés turístico en Cali.
        
        Args:
            lat: Latitud de referencia
            lng: Longitud de referencia
            interes: Tipo de interés (cultura, naturaleza, gastronomia)
            radio_metros: Radio de búsqueda
        
        Returns:
            Lista de puntos de interés
        """
        # Mapeo de intereses a tags de OSM
        interes_tags = {
            'cultura': ['tourism=museum', 'historic=monument', 'tourism=attraction', 'amenity=place_of_worship'],
            'naturaleza': ['leisure=park', 'natural=water', 'landuse=forest', 'tourism=zoo'],
            'gastronomia': ['amenity=restaurant', 'amenity=cafe', 'amenity=fast_food']
        }
        
        tags = interes_tags.get(interes, interes_tags['cultura'])
        
        all_results = []
        for tag in tags:
            params = {
                'lat': lat,
                'lon': lng,
                'radius': radio_metros,
                'format': 'json',
                'limit': 50,
                'featuretype': tag
            }
            
            try:
                await self.rate_limiter.wait_if_needed()
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/search",
                        params=params,
                        headers=self._get_headers(),
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        for item in data:
                            all_results.append({
                                'nombre': item.get('display_name', '').split(',')[0],
                                'lat': float(item.get('lat', 0)),
                                'lng': float(item.get('lon', 0)),
                                'tipo': tag.split('=')[1] if '=' in tag else tag,
                                'icono': item.get('icon', '📍')
                            })
            except Exception as e:
                logger.warning(f"Error buscando tag {tag}: {str(e)}")
                continue
        
        # Eliminar duplicados (mismo nombre y coordenadas cercanas)
        unique_results = {}
        for r in all_results:
            key = f"{r['nombre']}_{round(r['lat'], 4)}_{round(r['lng'], 4)}"
            if key not in unique_results:
                unique_results[key] = r
        
        return list(unique_results.values())


# =====================================================
# FUNCIONES DE AYUDA
# =====================================================

def _validar_coordenadas(lat: float, lng: float) -> bool:
    """Validar que las coordenadas estén en rangos válidos."""
    return -90 <= lat <= 90 and -180 <= lng <= 180


async def geocode_direccion(direccion: str) -> Optional[Tuple[float, float]]:
    """Helper rápido para geocodificar una dirección."""
    return await geocoding_osm.geocode(direccion)


async def reverse_geocode_coordenadas(lat: float, lng: float) -> Optional[str]:
    """Helper rápido para geocodificación inversa."""
    return await geocoding_osm.reverse_geocode(lat, lng)


# =====================================================
# INSTANCIA GLOBAL
# =====================================================

# Instancia global del servicio
geocoding_osm = GeocodingOSM()


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("=" * 50)
        print("Geocoding OSM - Prueba de funcionalidad")
        print("=" * 50)
        
        osm = GeocodingOSM()
        
        # Prueba 1: Geocodificar dirección
        print("\n📍 Prueba 1: Geocodificar 'Cristo Rey, Cali'")
        coords = await osm.geocode("Cristo Rey")
        if coords:
            print(f"   ✅ Coordenadas: ({coords[0]:.6f}, {coords[1]:.6f})")
        else:
            print("   ❌ No se encontró")
        
        # Prueba 2: Reverse geocoding
        if coords:
            print(f"\n📍 Prueba 2: Reverse geocoding de ({coords[0]:.6f}, {coords[1]:.6f})")
            direccion = await osm.reverse_geocode(coords[0], coords[1])
            if direccion:
                print(f"   ✅ Dirección: {direccion[:80]}...")
            else:
                print("   ❌ No se encontró dirección")
        
        # Prueba 3: Cache
        print("\n📍 Prueba 3: Segunda geocodificación (debería venir de cache)")
        import time
        start = time.time()
        coords2 = await osm.geocode("Cristo Rey")
        elapsed = time.time() - start
        print(f"   ✅ Respuesta en {elapsed:.3f}s (cache)")
        
        print("\n✅ Todas las pruebas completadas")
    
    asyncio.run(test())