"""
Servicio de Realidad Aumentada (AR) para LoCALIzate / LoCALIzate Backend
======================================================================

Maneja reconocimiento de lugares, geolocalización avanzada y 
visualización AR de puntos de interés turísticos en Cali.

Características:
    - Cálculo de distancia y azimuth entre puntos
    - Filtrado de lugares por campo de visión de la cámara
    - Generación de instrucciones visuales para AR
    - Integración con base de datos de lugares
"""

import math
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import ValidationException

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class LugarAR:
    """
    Lugar turístico con información optimizada para AR.
    
    Attributes:
        id: ID del lugar en la base de datos
        nombre: Nombre del lugar
        lat: Latitud
        lng: Longitud
        distancia_km: Distancia desde el usuario en kilómetros
        azimuth: Ángulo respecto al norte (0-360 grados)
        altura_msnm: Altitud sobre nivel del mar
        descripcion_corta: Descripción breve (máx 100 chars)
        imagen_url: URL de la imagen representativa
        rating: Calificación promedio (0-5)
        icono: Emoji o icono representativo
        horario: Horario de atención (opcional)
        es_destacado: Si es un lugar destacado
    """
    id: int
    nombre: str
    lat: float
    lng: float
    distancia_km: float
    azimuth: float
    altura_msnm: float = 0.0
    descripcion_corta: str = ""
    imagen_url: str = ""
    rating: float = 0.0
    icono: str = "📍"
    horario: Optional[str] = None
    es_destacado: bool = False
    
    @property
    def distancia_m(self) -> float:
        """Distancia en metros."""
        return self.distancia_km * 1000
    
    @property
    def distancia_formateada(self) -> str:
        """Distancia formateada para mostrar al usuario."""
        if self.distancia_km < 0.1:
            return f"{int(self.distancia_m)} m"
        return f"{self.distancia_km:.1f} km"
    
    @property
    def rating_stars(self) -> str:
        """Representación visual del rating en estrellas."""
        full = int(self.rating)
        half = self.rating - full >= 0.5
        empty = 5 - full - (1 if half else 0)
        return "★" * full + ("½" if half else "") + "☆" * empty
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para API."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "lat": self.lat,
            "lng": self.lng,
            "distancia_km": self.distancia_km,
            "distancia_m": self.distancia_m,
            "distancia_formateada": self.distancia_formateada,
            "azimuth": self.azimuth,
            "altura_msnm": self.altura_msnm,
            "descripcion": self.descripcion_corta,
            "imagen_url": self.imagen_url,
            "rating": self.rating,
            "rating_stars": self.rating_stars,
            "icono": self.icono,
            "horario": self.horario,
            "es_destacado": self.es_destacado
        }


class ARService:
    """
    Servicio de Realidad Aumentada.
    
    Responsabilidades:
        1. Calcular posiciones relativas entre usuario y lugares
        2. Filtrar lugares dentro del campo de visión de la cámara
        3. Generar instrucciones de navegación visual
        4. Ordenar lugares por distancia o relevancia
    """
    
    def __init__(self, radio_busqueda_km: float = 2.0):
        """
        Inicializar servicio AR.
        
        Args:
            radio_busqueda_km: Radio de búsqueda alrededor del usuario (default 2km)
        """
        self.radio_busqueda_km = radio_busqueda_km
        self._camara_fov_deg = 60  # Campo de visión típico de cámara smartphone
        logger.info(f"ARService inicializado con radio de búsqueda de {radio_busqueda_km}km")
    
    # =====================================================
    # CÁLCULOS GEOMÉTRICOS
    # =====================================================
    
    @staticmethod
    def calcular_distancia_haversine(
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Calcular distancia en kilómetros entre dos puntos usando fórmula de Haversine.
        
        Args:
            lat1, lon1: Coordenadas del primer punto
            lat2, lon2: Coordenadas del segundo punto
        
        Returns:
            Distancia en kilómetros
        """
        R = 6371  # Radio de la Tierra en km
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def calcular_azimuth(
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Calcular el ángulo (azimuth) desde punto1 hacia punto2.
        
        0° = Norte
        90° = Este  
        180° = Sur
        270° = Oeste
        
        Args:
            lat1, lon1: Coordenadas de origen
            lat2, lon2: Coordenadas de destino
        
        Returns:
            Ángulo en grados (0-360)
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        x = math.sin(delta_lon) * math.cos(lat2_rad)
        y = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
        
        azimuth = math.atan2(x, y)
        azimuth_deg = math.degrees(azimuth)
        
        return (azimuth_deg + 360) % 360  # Normalizar a 0-360
    
    @staticmethod
    def calcular_angulo_relativo(azimuth: float, heading: float) -> float:
        """
        Calcular ángulo relativo entre el azimuth del lugar y la dirección de la cámara.
        
        Args:
            azimuth: Ángulo del lugar respecto al norte
            heading: Dirección de la cámara (0-360)
        
        Returns:
            Ángulo relativo (0 = al frente, 90 = derecha, -90 = izquierda)
        """
        relativo = (azimuth - heading + 360) % 360
        if relativo > 180:
            relativo = relativo - 360
        return relativo
    
    # =====================================================
    # FILTRADO DE LUGARES PARA AR
    # =====================================================
    
    def lugares_cerca_para_ar(
        self, 
        lat_usuario: float, 
        lng_usuario: float,
        lugares_db: List[Dict[str, Any]],
        heading_telefono: Optional[float] = None,
        max_resultados: int = 20
    ) -> List[LugarAR]:
        """
        Encuentra lugares cercanos y los prepara para mostrar en AR.
        
        Args:
            lat_usuario: Latitud del usuario
            lng_usuario: Longitud del usuario
            lugares_db: Lista de lugares desde la base de datos
            heading_telefono: Dirección del teléfono (0-360 grados)
            max_resultados: Máximo número de resultados
        
        Returns:
            Lista de lugares enriquecidos con datos AR
        """
        lugares_cerca = []
        
        for lugar in lugares_db:
            # Extraer coordenadas
            lugar_lat = lugar.get('lat', lugar.get('latitud', 0))
            lugar_lng = lugar.get('lng', lugar.get('longitud', 0))
            
            # Calcular distancia
            distancia = self.calcular_distancia_haversine(
                lat_usuario, lng_usuario, lugar_lat, lugar_lng
            )
            
            # Filtrar por radio
            if distancia > self.radio_busqueda_km:
                continue
            
            # Calcular azimuth
            azimuth = self.calcular_azimuth(
                lat_usuario, lng_usuario, lugar_lat, lugar_lng
            )
            
            # Verificar si está en campo de visión si tenemos heading
            if heading_telefono is not None:
                angulo_relativo = self.calcular_angulo_relativo(azimuth, heading_telefono)
                # Solo mostrar si está dentro del campo de visión (±FOV/2 grados)
                if abs(angulo_relativo) > self._camara_fov_deg:
                    continue
            
            # Crear objeto LugarAR
            lugar_ar = LugarAR(
                id=lugar.get('id', 0),
                nombre=lugar.get('nombre', 'Lugar sin nombre'),
                lat=lugar_lat,
                lng=lugar_lng,
                distancia_km=round(distancia, 2),
                azimuth=round(azimuth, 1),
                altura_msnm=lugar.get('altura_msnm', lugar.get('altitud', 0)),
                descripcion_corta=lugar.get('descripcion_corta', lugar.get('descripcion', ''))[:100],
                imagen_url=lugar.get('imagen', lugar.get('imagen_principal', '')),
                rating=lugar.get('rating', 0),
                icono=lugar.get('icono', '📍'),
                horario=lugar.get('horario'),
                es_destacado=lugar.get('destacado', False)
            )
            lugares_cerca.append(lugar_ar)
        
        # Ordenar: primero destacados, luego por distancia
        lugares_cerca.sort(key=lambda x: (-x.es_destacado, x.distancia_km))
        
        return lugares_cerca[:max_resultados]
    
    # =====================================================
    # GENERACIÓN DE INSTRUCCIONES
    # =====================================================
    
    def generar_instruccion_ar(
        self, 
        lugar: LugarAR, 
        heading: float
    ) -> Dict[str, Any]:
        """
        Generar instrucción visual para AR basada en posición relativa.
        
        Args:
            lugar: Lugar con datos AR
            heading: Dirección actual de la cámara
        
        Returns:
            Instrucción con dirección, distancia y visualización
        """
        angulo_relativo = self.calcular_angulo_relativo(lugar.azimuth, heading)
        
        # Determinar dirección textual
        if abs(angulo_relativo) < 15:
            direccion = "🔴 AL FRENTE"
            direccion_corta = "↑ FRENTE"
        elif angulo_relativo < 0:
            if angulo_relativo > -45:
                direccion = "🟡 IZQUIERDA"
                direccion_corta = "← IZQ"
            else:
                direccion = "🟠 IZQUIERDA LEJOS"
                direccion_corta = "↙ IZQ"
        else:  # angulo_relativo > 0
            if angulo_relativo < 45:
                direccion = "🟢 DERECHA"
                direccion_corta = "→ DER"
            else:
                direccion = "🔵 DERECHA LEJOS"
                direccion_corta = "↘ DER"
        
        return {
            "id": lugar.id,
            "nombre": lugar.nombre,
            "icono": lugar.icono,
            "distancia_km": lugar.distancia_km,
            "distancia_formateada": lugar.distancia_formateada,
            "direccion": direccion,
            "direccion_corta": direccion_corta,
            "angulo_relativo": round(angulo_relativo, 1),
            "azimuth": lugar.azimuth,
            "descripcion": lugar.descripcion_corta,
            "rating": lugar.rating,
            "rating_stars": lugar.rating_stars,
            "imagen_url": lugar.imagen_url,
            "horario": lugar.horario
        }
    
    def generar_instrucciones_batch(
        self,
        lugares: List[LugarAR],
        heading: float,
        max_instrucciones: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generar instrucciones para múltiples lugares.
        
        Args:
            lugares: Lista de lugares AR
            heading: Dirección actual de la cámara
            max_instrucciones: Máximo número de instrucciones
        
        Returns:
            Lista de instrucciones ordenadas por relevancia
        """
        instrucciones = []
        for lugar in lugares[:max_instrucciones]:
            instrucciones.append(self.generar_instruccion_ar(lugar, heading))
        
        return instrucciones
    
    # =====================================================
    # ESTADÍSTICAS Y MÉTRICAS
    # =====================================================
    
    def get_estadisticas_cercania(
        self,
        lat_usuario: float,
        lng_usuario: float,
        lugares_db: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Obtener estadísticas de lugares cercanos.
        
        Returns:
            Diccionario con métricas: total, por interés, más cercano, etc.
        """
        lugares_con_distancia = []
        
        for lugar in lugares_db:
            lugar_lat = lugar.get('lat', lugar.get('latitud', 0))
            lugar_lng = lugar.get('lng', lugar.get('longitud', 0))
            
            distancia = self.calcular_distancia_haversine(
                lat_usuario, lng_usuario, lugar_lat, lugar_lng
            )
            
            lugares_con_distancia.append({
                "id": lugar.get('id'),
                "nombre": lugar.get('nombre'),
                "interes": lugar.get('interes'),
                "distancia_km": round(distancia, 2),
                "destacado": lugar.get('destacado', False)
            })
        
        # Ordenar por distancia
        lugares_con_distancia.sort(key=lambda x: x["distancia_km"])
        
        # Contar por interés
        conteo_intereses = {}
        for l in lugares_con_distancia:
            interes = l.get("interes", "otros")
            conteo_intereses[interes] = conteo_intereses.get(interes, 0) + 1
        
        # Encontrar más cercano
        mas_cercano = lugares_con_distancia[0] if lugares_con_distancia else None
        
        # Contar cerca
        muy_cerca = sum(1 for l in lugares_con_distancia if l["distancia_km"] < 0.5)
        cerca = sum(1 for l in lugares_con_distancia if l["distancia_km"] < 1.0)
        
        return {
            "total_cerca": len(lugares_con_distancia),
            "muy_cerca_500m": muy_cerca,
            "cerca_1km": cerca,
            "mas_cercano": mas_cercano,
            "conteo_por_interes": conteo_intereses,
            "radio_busqueda_km": self.radio_busqueda_km
        }


# =====================================================
# INSTANCIA GLOBAL
# =====================================================

# Instancia global del servicio AR
ar_service = ARService()


# =====================================================
# FUNCIÓN DE AYUDA PARA INTEGRACIÓN CON REPOSITORIOS
# =====================================================

async def obtener_lugares_ar_cerca(
    lugar_repo,
    lat_usuario: float,
    lng_usuario: float,
    heading: Optional[float] = None,
    radio_km: float = 2.0,
    max_resultados: int = 10
) -> List[Dict[str, Any]]:
    """
    Helper para obtener lugares AR cercanos desde el repositorio.
    
    Args:
        lugar_repo: Instancia de LugarRepository
        lat_usuario: Latitud del usuario
        lng_usuario: Longitud del usuario
        heading: Dirección de la cámara (opcional)
        radio_km: Radio de búsqueda
        max_resultados: Máximo de resultados
    
    Returns:
        Lista de instrucciones AR
    """
    # Obtener lugares activos desde BD
    lugares_db = await lugar_repo.get_all_active(limit=100)
    
    # Crear servicio con radio personalizado
    ar_svc = ARService(radio_busqueda_km=radio_km)
    
    # Filtrar y procesar
    lugares_ar = ar_svc.lugares_cerca_para_ar(
        lat_usuario, lng_usuario, lugares_db, heading, max_resultados
    )
    
    # Generar instrucciones si hay heading
    if heading is not None:
        return ar_svc.generar_instrucciones_batch(lugares_ar, heading, max_resultados)
    
    # Si no hay heading, devolver datos básicos
    return [lugar.to_dict() for lugar in lugares_ar]


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("AR Service - Prueba de funcionalidad")
    print("=" * 50)
    
    # Prueba 1: Crear servicio
    ar = ARService(radio_busqueda_km=2.0)
    print(f"\n✅ ARService inicializado. Radio: {ar.radio_busqueda_km}km")
    
    # Prueba 2: Cálculo de distancia
    distancia = ar.calcular_distancia_haversine(3.4516, -76.5320, 3.43587, -76.56490)
    print(f"📏 Distancia Centro Cali -> Cristo Rey: {distancia:.2f} km")
    
    # Prueba 3: Cálculo de azimuth
    azimuth = ar.calcular_azimuth(3.4516, -76.5320, 3.43587, -76.56490)
    print(f"🧭 Azimuth Centro -> Cristo Rey: {azimuth:.1f}°")
    
    # Prueba 4: Ángulo relativo
    angulo = ar.calcular_angulo_relativo(azimuth, 90)
    print(f"📐 Ángulo relativo (si miras al Este): {angulo:.1f}°")
    
    # Prueba 5: LugarAR
    lugar_test = LugarAR(
        id=1,
        nombre="Cristo Rey",
        lat=3.43587,
        lng=-76.56490,
        distancia_km=distancia,
        azimuth=azimuth,
        rating=4.7,
        icono="✝️"
    )
    print(f"\n📍 LugarAR creado: {lugar_test.nombre}")
    print(f"   Distancia: {lugar_test.distancia_formateada}")
    print(f"   Rating: {lugar_test.rating_stars}")
    
    # Prueba 6: Generar instrucción
    instruccion = ar.generar_instruccion_ar(lugar_test, 90)
    print(f"\n🗺️ Instrucción AR:")
    print(f"   Dirección: {instruccion['direccion']}")
    print(f"   Distancia: {instruccion['distancia_formateada']}")
    
    print("\n✅ ARService funcionando correctamente")