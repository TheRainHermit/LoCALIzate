"""
Optimizador de Rutas para LoCALIzate / CaliGuia Backend
========================================================

Sistema de optimización de rutas turísticas usando algoritmos de vecino más cercano.
Completamente gratuito, sin API externa (no requiere Google Maps ni OSRM).

Características:
    - Algoritmo del vecino más cercano para optimización de órden de visita
    - Cálculo de distancias con fórmula de Haversine
    - Estimación de tiempos por modo de transporte
    - Generación de instrucciones paso a paso
    - Soporte para puntos de inicio personalizados (ubicación del usuario)
"""

import math
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


# =====================================================
# ENUMS Y CONSTANTES
# =====================================================

class ModoTransporte(str, Enum):
    """Modos de transporte para cálculo de tiempos."""
    CAMINANDO = "walking"
    BICICLETA = "biking"
    AUTO = "driving"
    TRANSPORTE_PUBLICO = "public"
    
    @property
    def velocidad_kmh(self) -> float:
        """Velocidad promedio en km/h por modo."""
        velocidades = {
            ModoTransporte.CAMINANDO: 5.0,
            ModoTransporte.BICICLETA: 15.0,
            ModoTransporte.AUTO: 30.0,
            ModoTransporte.TRANSPORTE_PUBLICO: 20.0
        }
        return velocidades.get(self, 5.0)
    
    @property
    def nombre_es(self) -> str:
        """Nombre en español."""
        nombres = {
            ModoTransporte.CAMINANDO: "Caminando",
            ModoTransporte.BICICLETA: "En bicicleta",
            ModoTransporte.AUTO: "En auto",
            ModoTransporte.TRANSPORTE_PUBLICO: "Transporte público"
        }
        return nombres.get(self, "Caminando")


@dataclass
class PuntoRuta:
    """Punto en una ruta optimizada."""
    id: int
    nombre: str
    lat: float
    lng: float
    orden: int
    distancia_desde_anterior_km: float = 0.0
    tiempo_desde_anterior_min: int = 0
    distancia_acumulada_km: float = 0.0
    tiempo_acumulado_min: int = 0
    instruccion: str = ""
    
    @property
    def distancia_formateada(self) -> str:
        """Distancia formateada para mostrar."""
        if self.distancia_desde_anterior_km < 0.1:
            return f"{int(self.distancia_desde_anterior_km * 1000)} m"
        return f"{self.distancia_desde_anterior_km:.1f} km"
    
    @property
    def tiempo_formateado(self) -> str:
        """Tiempo formateado para mostrar."""
        if self.tiempo_desde_anterior_min < 60:
            return f"{self.tiempo_desde_anterior_min} min"
        horas = self.tiempo_desde_anterior_min // 60
        minutos = self.tiempo_desde_anterior_min % 60
        return f"{horas}h {minutos}min"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para API."""
        return {
            "orden": self.orden,
            "id": self.id,
            "nombre": self.nombre,
            "lat": self.lat,
            "lng": self.lng,
            "distancia_desde_anterior_km": self.distancia_desde_anterior_km,
            "distancia_formateada": self.distancia_formateada,
            "tiempo_desde_anterior_min": self.tiempo_desde_anterior_min,
            "tiempo_formateado": self.tiempo_formateado,
            "distancia_acumulada_km": round(self.distancia_acumulada_km, 2),
            "tiempo_acumulado_min": self.tiempo_acumulado_min,
            "instruccion": self.instruccion
        }


@dataclass
class RutaOptimizada:
    """Resultado completo de una ruta optimizada."""
    puntos: List[PuntoRuta]
    distancia_total_km: float
    tiempo_total_min: int
    modo_transporte: ModoTransporte
    punto_inicio: Optional[Dict[str, Any]] = None
    advertencias: List[str] = field(default_factory=list)
    
    @property
    def tiempo_formateado(self) -> str:
        """Tiempo total formateado."""
        if self.tiempo_total_min < 60:
            return f"{self.tiempo_total_min} min"
        horas = self.tiempo_total_min // 60
        minutos = self.tiempo_total_min % 60
        return f"{horas}h {minutos}min"
    
    @property
    def cantidad_puntos(self) -> int:
        """Número de puntos en la ruta."""
        return len(self.puntos)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para API."""
        return {
            "puntos": [p.to_dict() for p in self.puntos],
            "distancia_total_km": round(self.distancia_total_km, 2),
            "tiempo_total_min": self.tiempo_total_min,
            "tiempo_formateado": self.tiempo_formateado,
            "cantidad_puntos": self.cantidad_puntos,
            "modo_transporte": self.modo_transporte.value,
            "modo_transporte_nombre": self.modo_transporte.nombre_es,
            "punto_inicio": self.punto_inicio,
            "advertencias": self.advertencias
        }


# =====================================================
# FUNCIONES DE CÁLCULO
# =====================================================

def calcular_distancia_haversine(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float
) -> float:
    """
    Calcular distancia en kilómetros usando fórmula de Haversine.
    
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


def calcular_tiempo_estimado(
    distancia_km: float, 
    modo: ModoTransporte = ModoTransporte.CAMINANDO
) -> int:
    """
    Calcular tiempo estimado en minutos basado en distancia y modo de transporte.
    
    Args:
        distancia_km: Distancia en kilómetros
        modo: Modo de transporte
    
    Returns:
        Tiempo en minutos
    """
    tiempo_horas = distancia_km / modo.velocidad_kmh
    return int(tiempo_horas * 60)


def obtener_direccion_cardinal(azimuth: float) -> str:
    """
    Obtener dirección cardinal a partir de un ángulo.
    
    Args:
        azimuth: Ángulo en grados (0-360, 0 = Norte)
    
    Returns:
        Dirección cardinal (N, NE, E, SE, S, SO, O, NO)
    """
    direcciones = [
        ("N", 0, 22.5),
        ("NE", 22.5, 67.5),
        ("E", 67.5, 112.5),
        ("SE", 112.5, 157.5),
        ("S", 157.5, 202.5),
        ("SO", 202.5, 247.5),
        ("O", 247.5, 292.5),
        ("NO", 292.5, 337.5),
        ("N", 337.5, 360)
    ]
    
    for direccion, inicio, fin in direcciones:
        if inicio <= azimuth < fin:
            return direccion
    
    return "N"


def calcular_azimuth(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float
) -> float:
    """
    Calcular azimuth (ángulo) entre dos puntos.
    
    Args:
        lat1, lon1: Coordenadas de origen
        lat2, lon2: Coordenadas de destino
    
    Returns:
        Ángulo en grados (0-360, 0 = Norte)
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)
    
    x = math.sin(delta_lon) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
    
    azimuth = math.atan2(x, y)
    azimuth_deg = math.degrees(azimuth)
    
    return (azimuth_deg + 360) % 360


# =====================================================
# ALGORITMO DE OPTIMIZACIÓN
# =====================================================

def optimizar_ruta(
    lugares: List[Dict[str, Any]],
    origen_lat: float,
    origen_lng: float,
    modo: ModoTransporte = ModoTransporte.CAMINANDO
) -> RutaOptimizada:
    """
    Optimizar orden de visita usando algoritmo del vecino más cercano.
    
    Args:
        lugares: Lista de lugares con id, nombre, lat, lng
        origen_lat: Latitud del punto de inicio
        origen_lng: Longitud del punto de inicio
        modo: Modo de transporte
    
    Returns:
        RutaOptimizada con puntos ordenados y métricas
    """
    if not lugares:
        return RutaOptimizada(
            puntos=[],
            distancia_total_km=0,
            tiempo_total_min=0,
            modo_transporte=modo,
            advertencias=["No hay lugares para visitar"]
        )
    
    advertencias = []
    
    # Validar lugares
    lugares_validos = []
    for lugar in lugares:
        lat = lugar.get('lat', lugar.get('latitud'))
        lng = lugar.get('lng', lugar.get('longitud'))
        
        if lat is None or lng is None:
            advertencias.append(f"Lugar '{lugar.get('nombre', 'Desconocido')}' no tiene coordenadas válidas")
            continue
        
        lugares_validos.append({
            'id': lugar.get('id'),
            'nombre': lugar.get('nombre'),
            'lat': lat,
            'lng': lng
        })
    
    if not lugares_validos:
        return RutaOptimizada(
            puntos=[],
            distancia_total_km=0,
            tiempo_total_min=0,
            modo_transporte=modo,
            advertencias=["Ningún lugar tenía coordenadas válidas"]
        )
    
    # Algoritmo del vecino más cercano
    no_visitados = lugares_validos.copy()
    puntos_ordenados = []
    posicion_actual = {"lat": origen_lat, "lng": origen_lng}
    distancia_total = 0.0
    tiempo_total = 0
    
    for orden in range(len(no_visitados)):
        # Encontrar lugar más cercano
        idx_cercano = 0
        dist_min = calcular_distancia_haversine(
            posicion_actual["lat"], posicion_actual["lng"],
            no_visitados[0]["lat"], no_visitados[0]["lng"]
        )
        
        for i in range(1, len(no_visitados)):
            dist = calcular_distancia_haversine(
                posicion_actual["lat"], posicion_actual["lng"],
                no_visitados[i]["lat"], no_visitados[i]["lng"]
            )
            if dist < dist_min:
                dist_min = dist
                idx_cercano = i
        
        lugar_seleccionado = no_visitados.pop(idx_cercano)
        tiempo = calcular_tiempo_estimado(dist_min, modo)
        
        # Calcular azimuth para instrucción
        azimuth = calcular_azimuth(
            posicion_actual["lat"], posicion_actual["lng"],
            lugar_seleccionado["lat"], lugar_seleccionado["lng"]
        )
        direccion = obtener_direccion_cardinal(azimuth)
        
        # Actualizar acumulados
        distancia_total += dist_min
        tiempo_total += tiempo
        
        instruccion = obtener_instruccion_simple(
            lugar_seleccionado["nombre"],
            dist_min,
            direccion,
            modo
        )
        
        punto = PuntoRuta(
            id=lugar_seleccionado["id"],
            nombre=lugar_seleccionado["nombre"],
            lat=lugar_seleccionado["lat"],
            lng=lugar_seleccionado["lng"],
            orden=orden + 1,
            distancia_desde_anterior_km=round(dist_min, 2),
            tiempo_desde_anterior_min=tiempo,
            distancia_acumulada_km=round(distancia_total, 2),
            tiempo_acumulado_min=tiempo_total,
            instruccion=instruccion
        )
        puntos_ordenados.append(punto)
        
        posicion_actual = lugar_seleccionado
    
    return RutaOptimizada(
        puntos=puntos_ordenados,
        distancia_total_km=distancia_total,
        tiempo_total_min=tiempo_total,
        modo_transporte=modo,
        advertencias=advertencias
    )


def optimizar_ruta_con_retorno(
    lugares: List[Dict[str, Any]],
    origen_lat: float,
    origen_lng: float,
    modo: ModoTransporte = ModoTransporte.CAMINANDO
) -> RutaOptimizada:
    """
    Optimizar ruta con retorno al punto de inicio (circuito cerrado).
    
    Args:
        lugares: Lista de lugares a visitar
        origen_lat, origen_lng: Punto de inicio y fin
        modo: Modo de transporte
    
    Returns:
        RutaOptimizada incluyendo retorno al inicio
    """
    ruta = optimizar_ruta(lugares, origen_lat, origen_lng, modo)
    
    if not ruta.puntos:
        return ruta
    
    # Calcular distancia de regreso desde el último punto
    ultimo_punto = ruta.puntos[-1]
    distancia_retorno = calcular_distancia_haversine(
        ultimo_punto.lat, ultimo_punto.lng,
        origen_lat, origen_lng
    )
    tiempo_retorno = calcular_tiempo_estimado(distancia_retorno, modo)
    
    ruta.distancia_total_km += distancia_retorno
    ruta.tiempo_total_min += tiempo_retorno
    
    ruta.advertencias.append(f"Retorno al inicio: {distancia_retorno:.1f} km, {tiempo_retorno} min")
    
    return ruta


# =====================================================
# FUNCIONES DE INSTRUCCIONES
# =====================================================

def obtener_instruccion_simple(
    destino_nombre: str,
    distancia_km: float,
    direccion: str,
    modo: ModoTransporte = ModoTransporte.CAMINANDO
) -> str:
    """
    Generar instrucción simple para navegar entre puntos.
    
    Args:
        destino_nombre: Nombre del destino
        distancia_km: Distancia en kilómetros
        direccion: Dirección cardinal
        modo: Modo de transporte
    
    Returns:
        Instrucción legible
    """
    emoji_transporte = {
        ModoTransporte.CAMINANDO: "🚶",
        ModoTransporte.BICICLETA: "🚲",
        ModoTransporte.AUTO: "🚗",
        ModoTransporte.TRANSPORTE_PUBLICO: "🚌"
    }
    
    distancia_texto = f"{distancia_km:.1f} km" if distancia_km >= 0.1 else f"{int(distancia_km * 1000)} m"
    
    return f"{emoji_transporte.get(modo, '📍')} {distancia_texto} hacia el {direccion} hasta {destino_nombre}"


def obtener_instrucciones_completas(
    ruta: RutaOptimizada,
    origen_nombre: str = "Tu ubicación"
) -> List[str]:
    """
    Generar instrucciones completas paso a paso.
    
    Args:
        ruta: Ruta optimizada
        origen_nombre: Nombre del punto de inicio
    
    Returns:
        Lista de instrucciones legibles
    """
    instrucciones = []
    
    # Instrucción inicial
    instrucciones.append(f"📍 Desde {origen_nombre}:")
    
    for punto in ruta.puntos:
        if punto.orden == 1:
            instrucciones.append(f"  {punto.instruccion}")
        else:
            instrucciones.append(f"  Luego {punto.instruccion.lower()}")
        
        # Añadir tiempo acumulado
        instrucciones.append(f"     ⏱️ Llegada: ~{punto.tiempo_formateado}")
    
    # Resumen final
    instrucciones.append("")
    instrucciones.append(f"📊 Resumen del recorrido:")
    instrucciones.append(f"   • Distancia total: {ruta.distancia_total_km:.1f} km")
    instrucciones.append(f"   • Tiempo total: {ruta.tiempo_formateado}")
    instrucciones.append(f"   • Lugares a visitar: {ruta.cantidad_puntos}")
    
    return instrucciones


def obtener_instrucciones_simples(origen_nombre: str, destino_nombre: str, distancia_km: float) -> List[str]:
    """
    Generar instrucciones simples para navegar entre puntos.
    
    Esta función es un alias simplificado de obtener_instrucciones_completas
    para casos donde solo se necesitan instrucciones básicas entre dos puntos.
    
    Args:
        origen_nombre: Nombre del punto de origen
        destino_nombre: Nombre del punto de destino
        distancia_km: Distancia en kilómetros
    
    Returns:
        Lista de instrucciones paso a paso
    """
    tiempo_min = calcular_tiempo_estimado(distancia_km, ModoTransporte.CAMINANDO)
    
    instrucciones = [
        f"📍 Desde {origen_nombre}",
        f"🚶 Camina {distancia_km:.1f} km hacia {destino_nombre}",
        f"⏱️ Aproximadamente {tiempo_min} minutos caminando",
        f"🎯 Llegarás a {destino_nombre}"
    ]
    
    return instrucciones


# =====================================================
# FUNCIONES DE ANÁLISIS
# =====================================================

def calcular_matriz_distancias(
    lugares: List[Dict[str, Any]]
) -> List[List[float]]:
    """
    Calcular matriz de distancias entre todos los lugares.
    
    Args:
        lugares: Lista de lugares con coordenadas
    
    Returns:
        Matriz de distancias (km)
    """
    n = len(lugares)
    matriz = [[0.0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            if i != j:
                lat1 = lugares[i].get('lat', lugares[i].get('latitud'))
                lng1 = lugares[i].get('lng', lugares[i].get('longitud'))
                lat2 = lugares[j].get('lat', lugares[j].get('latitud'))
                lng2 = lugares[j].get('lng', lugares[j].get('longitud'))
                
                matriz[i][j] = calcular_distancia_haversine(lat1, lng1, lat2, lng2)
    
    return matriz


def encontrar_lugar_mas_cercano(
    lugares: List[Dict[str, Any]],
    lat: float,
    lng: float
) -> Optional[Dict[str, Any]]:
    """
    Encontrar el lugar más cercano a una ubicación.
    
    Args:
        lugares: Lista de lugares
        lat, lng: Coordenadas de referencia
    
    Returns:
        Lugar más cercano o None
    """
    if not lugares:
        return None
    
    cercano = min(
        lugares,
        key=lambda l: calcular_distancia_haversine(
            lat, lng,
            l.get('lat', l.get('latitud')),
            l.get('lng', l.get('longitud'))
        )
    )
    
    return cercano


def calcular_tiempo_total_visita(
    lugares: List[Dict[str, Any]],
    tiempo_por_lugar_min: int = 60
) -> int:
    """
    Calcular tiempo total de visita incluyendo desplazamientos aproximados.
    
    Args:
        lugares: Lista de lugares
        tiempo_por_lugar_min: Tiempo estimado por lugar
    
    Returns:
        Tiempo total en minutos
    """
    if len(lugares) <= 1:
        return len(lugares) * tiempo_por_lugar_min
    
    tiempo_total = 0
    tiempo_visita = len(lugares) * tiempo_por_lugar_min
    
    # Calcular distancia total aproximada (asumiendo orden dado)
    distancia_total = 0
    for i in range(len(lugares) - 1):
        lat1 = lugares[i].get('lat', lugares[i].get('latitud'))
        lng1 = lugares[i].get('lng', lugares[i].get('longitud'))
        lat2 = lugares[i + 1].get('lat', lugares[i + 1].get('latitud'))
        lng2 = lugares[i + 1].get('lng', lugares[i + 1].get('longitud'))
        
        distancia_total += calcular_distancia_haversine(lat1, lng1, lat2, lng2)
    
    tiempo_desplazamiento = calcular_tiempo_estimado(distancia_total)
    tiempo_total = tiempo_visita + tiempo_desplazamiento
    
    return tiempo_total


# =====================================================
# EXPORTS
# =====================================================

__all__ = [
    "ModoTransporte",
    "PuntoRuta",
    "RutaOptimizada",
    "calcular_distancia_haversine",
    "calcular_tiempo_estimado",
    "calcular_azimuth",
    "obtener_direccion_cardinal",
    "optimizar_ruta",
    "optimizar_ruta_con_retorno",
    "obtener_instruccion_simple",
    "obtener_instrucciones_completas",
    "obtener_instrucciones_simples",
    "calcular_matriz_distancias",
    "encontrar_lugar_mas_cercano",
    "calcular_tiempo_total_visita",
]


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Optimizador de Rutas - Prueba de funcionalidad")
    print("=" * 50)
    
    # Lugares de prueba (coordenadas reales de Cali)
    lugares_prueba = [
        {"id": 1, "nombre": "Cristo Rey", "lat": 3.43587, "lng": -76.56490},
        {"id": 2, "nombre": "El Gato del Río", "lat": 3.45156, "lng": -76.54297},
        {"id": 3, "nombre": "Iglesia La Ermita", "lat": 3.4520, "lng": -76.53201},
    ]
    
    # Centro de Cali como punto de inicio
    origen = {"lat": 3.4516, "lng": -76.5320}
    
    print("\n📍 Punto de inicio: Centro de Cali")
    print("📍 Lugares a visitar:")
    for l in lugares_prueba:
        print(f"   - {l['nombre']}")
    
    # Prueba 1: Optimización caminando
    print("\n" + "=" * 30)
    print("Prueba 1: Optimización caminando")
    ruta = optimizar_ruta(lugares_prueba, origen["lat"], origen["lng"])
    
    print(f"\n✅ Ruta optimizada ({ruta.modo_transporte.nombre_es}):")
    for punto in ruta.puntos:
        print(f"   {punto.orden}. {punto.nombre}")
        print(f"      📏 {punto.distancia_formateada}")
        print(f"      ⏱️ {punto.tiempo_formateado}")
        print(f"      🧭 {punto.instruccion}")
    
    print(f"\n📊 Total: {ruta.distancia_total_km:.1f} km, {ruta.tiempo_formateado}")
    
    # Prueba 2: Modo auto
    print("\n" + "=" * 30)
    print("Prueba 2: Optimización en auto")
    ruta_auto = optimizar_ruta(lugares_prueba, origen["lat"], origen["lng"], ModoTransporte.AUTO)
    print(f"✅ Tiempo en auto: {ruta_auto.tiempo_formateado} (vs {ruta.tiempo_formateado} caminando)")
    
    # Prueba 3: Instrucciones completas
    print("\n" + "=" * 30)
    print("Prueba 3: Instrucciones paso a paso")
    instrucciones = obtener_instrucciones_completas(ruta, "Centro de Cali")
    for inst in instrucciones:
        print(f"   {inst}")
    
    # Prueba 4: Instrucciones simples
    print("\n" + "=" * 30)
    print("Prueba 4: Instrucciones simples")
    instrucciones_simples = obtener_instrucciones_simples("Centro de Cali", "Cristo Rey", 5.2)
    for inst in instrucciones_simples:
        print(f"   {inst}")
    
    print("\n✅ Optimizador de rutas funcionando correctamente")