"""
Sistema de Recomendaciones para LoCALIzate / LoCALIzate Backend
==============================================================

Servicio inteligente de recomendaciones de lugares turísticos basado en:
    - Intereses del usuario
    - Historial de visitas y favoritos
    - Calificaciones y reseñas
    - Popularidad y tendencias
    - Proximidad geográfica

Características:
    - Recomendaciones personalizadas por intereses
    - Lugares similares (basado en categoría y rating)
    - Lugares populares y en tendencia
    - Recomendaciones híbridas (colaborativas + contenido)
"""

import logging
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import Counter

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


# =====================================================
# ENUMS Y CONSTANTES
# =====================================================

class TipoRecomendacion(str, Enum):
    """Tipos de recomendaciones disponibles."""
    POR_INTERES = "por_interes"
    POPULARES = "populares"
    TENDENCIA = "tendencia"
    SIMILARES = "similares"
    PROXIMOS = "proximos"
    PERSONALIZADAS = "personalizadas"
    NUEVOS = "nuevos"
    MEJOR_CALIFICADOS = "mejor_calificados"


@dataclass
class Recomendacion:
    """
    Recomendación de un lugar turístico.
    
    Attributes:
        lugar_id: ID del lugar
        nombre: Nombre del lugar
        puntaje: Puntaje de relevancia (0-100)
        razon: Razón de la recomendación
        categoria: Categoría del lugar
        rating: Calificación promedio
        distancia_km: Distancia desde el usuario (opcional)
    """
    lugar_id: int
    nombre: str
    puntaje: float
    razon: str
    categoria: str
    rating: float
    distancia_km: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para API."""
        return {
            "id": self.lugar_id,
            "nombre": self.nombre,
            "puntaje": round(self.puntaje, 1),
            "razon": self.razon,
            "categoria": self.categoria,
            "rating": self.rating,
            "distancia_km": self.distancia_km
        }


# =====================================================
# SERVICIO PRINCIPAL
# =====================================================

class RecommendationService:
    """
    Servicio de recomendaciones de lugares turísticos.
    
    Responsabilidades:
        1. Generar recomendaciones basadas en intereses del usuario
        2. Encontrar lugares similares a uno dado
        3. Obtener lugares populares y en tendencia
        4. Recomendaciones personalizadas híbridas
    """
    
    def __init__(self):
        """Inicializar servicio de recomendaciones."""
        # Pesos para diferentes factores (0-1)
        self.pesos = {
            "rating": 0.35,
            "popularidad": 0.25,
            "similitud_intereses": 0.25,
            "novedad": 0.15
        }
        
        # Lugares en tendencia (últimos días)
        self.trending_window_days = 7
        
        # Cache de resultados (evitar recomendar lo mismo)
        self.recommendation_cache = {}
        
        logger.info("RecommendationService inicializado correctamente")
    
    # =====================================================
    # RECOMENDACIONES POR INTERÉS
    # =====================================================
    
    async def recomendar_por_interes(
        self,
        lugar_repo,
        interes: str,
        limit: int = 10,
        exclude_ids: Optional[List[int]] = None
    ) -> List[Recomendacion]:
        """
        Recomendar lugares basados en un interés específico.
        
        Args:
            lugar_repo: Repositorio de lugares
            interes: Interés (cultura, naturaleza, gastronomia, salsa, aventura)
            limit: Máximo número de recomendaciones
            exclude_ids: IDs de lugares a excluir
        
        Returns:
            Lista de recomendaciones
        """
        try:
            # Obtener lugares del interés
            lugares = await lugar_repo.get_by_interes(interes, limit=50)
            
            if not lugares:
                logger.warning(f"No hay lugares para el interés: {interes}")
                return []
            
            # Filtrar excluidos
            if exclude_ids:
                lugares = [l for l in lugares if l.get('id') not in exclude_ids]
            
            # Calcular puntaje y generar recomendaciones
            recomendaciones = []
            for lugar in lugares[:limit]:
                # Puntaje basado en rating y destacado
                puntaje = lugar.get('rating', 0) * 10
                if lugar.get('destacado'):
                    puntaje += 10
                
                recomendacion = Recomendacion(
                    lugar_id=lugar.get('id'),
                    nombre=lugar.get('nombre'),
                    puntaje=min(100, puntaje),
                    razon=f"Lugar destacado de {self._get_interes_nombre(interes)} en Cali",
                    categoria=interes,
                    rating=lugar.get('rating', 0)
                )
                recomendaciones.append(recomendacion)
            
            # Ordenar por puntaje
            recomendaciones.sort(key=lambda x: x.puntaje, reverse=True)
            
            return recomendaciones[:limit]
            
        except Exception as e:
            logger.error(f"Error en recomendar_por_interes: {str(e)}")
            return []
    
    async def recomendar_por_intereses_usuario(
        self,
        usuario_repo,
        lugar_repo,
        usuario_id: str,
        limit: int = 10,
        exclude_ids: Optional[List[int]] = None
    ) -> List[Recomendacion]:
        """
        Recomendar lugares basados en los intereses del usuario.
        
        Args:
            usuario_repo: Repositorio de usuarios
            lugar_repo: Repositorio de lugares
            usuario_id: ID del usuario
            limit: Máximo número de recomendaciones
            exclude_ids: IDs de lugares a excluir
        
        Returns:
            Lista de recomendaciones personalizadas
        """
        try:
            # Obtener intereses del usuario
            intereses = await usuario_repo.get_intereses(usuario_id)
            
            if not intereses:
                # Si no tiene intereses, recomendar populares
                return await self.recomendar_populares(lugar_repo, limit)
            
            # Obtener recomendaciones por cada interés
            todas_recomendaciones = []
            for interes in intereses:
                recs = await self.recomendar_por_interes(
                    lugar_repo, interes, limit=20, exclude_ids=exclude_ids
                )
                todas_recomendaciones.extend(recs)
            
            # Eliminar duplicados y ordenar por puntaje
            unique_recs = {}
            for rec in todas_recomendaciones:
                if rec.lugar_id not in unique_recs or rec.puntaje > unique_recs[rec.lugar_id].puntaje:
                    unique_recs[rec.lugar_id] = rec
            
            resultados = list(unique_recs.values())
            resultados.sort(key=lambda x: x.puntaje, reverse=True)
            
            # Actualizar razones con los intereses específicos
            for rec in resultados[:limit]:
                rec.razon = f"Basado en tus intereses de {rec.categoria}"
            
            return resultados[:limit]
            
        except Exception as e:
            logger.error(f"Error en recomendar_por_intereses_usuario: {str(e)}")
            return []
    
    # =====================================================
    # RECOMENDACIONES POR POPULARIDAD
    # =====================================================
    
    async def recomendar_populares(
        self,
        lugar_repo,
        limit: int = 10,
        exclude_ids: Optional[List[int]] = None
    ) -> List[Recomendacion]:
        """
        Recomendar lugares más populares (mayor rating y reseñas).
        
        Args:
            lugar_repo: Repositorio de lugares
            limit: Máximo número de recomendaciones
            exclude_ids: IDs de lugares a excluir
        
        Returns:
            Lista de lugares populares
        """
        try:
            lugares = await lugar_repo.get_popular(limit=30)
            
            if not lugares:
                return []
            
            # Filtrar excluidos
            if exclude_ids:
                lugares = [l for l in lugares if l.get('id') not in exclude_ids]
            
            recomendaciones = []
            for lugar in lugares[:limit]:
                puntaje = lugar.get('rating', 0) * 10
                if lugar.get('rating_count', 0) > 100:
                    puntaje += 10  # Bonus por muchas reseñas
                
                recomendacion = Recomendacion(
                    lugar_id=lugar.get('id'),
                    nombre=lugar.get('nombre'),
                    puntaje=min(100, puntaje),
                    razon="Uno de los lugares más populares entre los visitantes",
                    categoria=lugar.get('interes', 'general'),
                    rating=lugar.get('rating', 0)
                )
                recomendaciones.append(recomendacion)
            
            return recomendaciones[:limit]
            
        except Exception as e:
            logger.error(f"Error en recomendar_populares: {str(e)}")
            return []
    
    async def recomendar_tendencias(
        self,
        lugar_repo,
        limit: int = 10,
        exclude_ids: Optional[List[int]] = None
    ) -> List[Recomendacion]:
        """
        Recomendar lugares en tendencia (basado en visitas recientes).
        
        Args:
            lugar_repo: Repositorio de lugares
            limit: Máximo número de recomendaciones
            exclude_ids: IDs de lugares a excluir
        
        Returns:
            Lista de lugares en tendencia
        """
        try:
            # Obtener lugares destacados y con mejor rating
            lugares = await lugar_repo.get_destacados(limit=30)
            
            if not lugares:
                lugares = await lugar_repo.get_all_active(limit=30)
            
            if not lugares:
                return []
            
            # Filtrar excluidos
            if exclude_ids:
                lugares = [l for l in lugares if l.get('id') not in exclude_ids]
            
            recomendaciones = []
            for lugar in lugares[:limit]:
                # Puntaje basado en rating + aleatorio para simular tendencia
                puntaje_base = lugar.get('rating', 0) * 10
                # Factor tendencia: lugares recién agregados o destacados
                factor_tendencia = 15 if lugar.get('destacado') else 5
                puntaje = puntaje_base + factor_tendencia
                
                recomendacion = Recomendacion(
                    lugar_id=lugar.get('id'),
                    nombre=lugar.get('nombre'),
                    puntaje=min(100, puntaje),
                    razon="En tendencia ahora en Cali 🔥",
                    categoria=lugar.get('interes', 'general'),
                    rating=lugar.get('rating', 0)
                )
                recomendaciones.append(recomendacion)
            
            return recomendaciones[:limit]
            
        except Exception as e:
            logger.error(f"Error en recomendar_tendencias: {str(e)}")
            return []
    
    # =====================================================
    # RECOMENDACIONES POR SIMILITUD
    # =====================================================
    
    async def recomendar_similares(
        self,
        lugar_repo,
        lugar_id: int,
        limit: int = 5,
        exclude_ids: Optional[List[int]] = None
    ) -> List[Recomendacion]:
        """
        Recomendar lugares similares a uno dado.
        
        Args:
            lugar_repo: Repositorio de lugares
            lugar_id: ID del lugar de referencia
            limit: Máximo número de recomendaciones
            exclude_ids: IDs de lugares a excluir
        
        Returns:
            Lista de lugares similares
        """
        try:
            # Obtener lugar original
            lugar_original = await lugar_repo.get_by_id(lugar_id)
            if not lugar_original:
                logger.warning(f"Lugar {lugar_id} no encontrado")
                return []
            
            interes = lugar_original.get('interes')
            rating = lugar_original.get('rating', 0)
            
            # Obtener lugares del mismo interés
            lugares = await lugar_repo.get_by_interes(interes, limit=30)
            
            if not lugares:
                return []
            
            # Filtrar el mismo lugar y excluidos
            exclude = [lugar_id]
            if exclude_ids:
                exclude.extend(exclude_ids)
            
            lugares = [l for l in lugares if l.get('id') not in exclude]
            
            # Calcular similitud
            recomendaciones = []
            for lugar in lugares:
                # Similitud por rating (cercano al original)
                diff_rating = abs(lugar.get('rating', 0) - rating)
                puntaje_rating = 20 * (1 - min(1, diff_rating / 5))
                
                # Similitud por destacado
                puntaje_destacado = 10 if lugar.get('destacado') else 0
                
                # Similitud por popularidad
                puntaje_popular = min(15, lugar.get('rating_count', 0) / 20)
                
                puntaje = puntaje_rating + puntaje_destacado + puntaje_popular
                
                recomendacion = Recomendacion(
                    lugar_id=lugar.get('id'),
                    nombre=lugar.get('nombre'),
                    puntaje=min(100, puntaje),
                    razon=f"Similar a {lugar_original.get('nombre')} - mismo estilo",
                    categoria=interes,
                    rating=lugar.get('rating', 0)
                )
                recomendaciones.append(recomendacion)
            
            recomendaciones.sort(key=lambda x: x.puntaje, reverse=True)
            
            return recomendaciones[:limit]
            
        except Exception as e:
            logger.error(f"Error en recomendar_similares: {str(e)}")
            return []
    
    # =====================================================
    # RECOMENDACIONES POR PROXIMIDAD
    # =====================================================
    
    async def recomendar_proximos(
        self,
        lugar_repo,
        lat: float,
        lng: float,
        limit: int = 10,
        interes: Optional[str] = None,
        exclude_ids: Optional[List[int]] = None
    ) -> List[Recomendacion]:
        """
        Recomendar lugares cercanos a una ubicación.
        
        Args:
            lugar_repo: Repositorio de lugares
            lat: Latitud de referencia
            lng: Longitud de referencia
            limit: Máximo número de recomendaciones
            interes: Filtrar por interés (opcional)
            exclude_ids: IDs de lugares a excluir
        
        Returns:
            Lista de lugares cercanos recomendados
        """
        try:
            from app.services.optimizador_rutas import calcular_distancia_haversine
            
            # Obtener lugares cercanos
            lugares = await lugar_repo.get_nearby(lat, lng, radio_km=5.0, interes=interes, limit=30)
            
            if not lugares:
                return []
            
            # Filtrar excluidos
            if exclude_ids:
                lugares = [l for l in lugares if l.get('id') not in exclude_ids]
            
            recomendaciones = []
            for lugar in lugares[:limit]:
                distancia = lugar.get('distancia_km', 0)
                
                # Puntaje: más cerca = mejor, combinado con rating
                puntaje_distancia = max(0, 40 - (distancia * 8))
                puntaje_rating = lugar.get('rating', 0) * 10
                puntaje = puntaje_distancia + puntaje_rating
                
                razon = f"A solo {self._formatear_distancia(distancia)} de ti"
                
                recomendacion = Recomendacion(
                    lugar_id=lugar.get('id'),
                    nombre=lugar.get('nombre'),
                    puntaje=min(100, puntaje),
                    razon=razon,
                    categoria=lugar.get('interes', 'general'),
                    rating=lugar.get('rating', 0),
                    distancia_km=distancia
                )
                recomendaciones.append(recomendacion)
            
            recomendaciones.sort(key=lambda x: x.puntaje, reverse=True)
            
            return recomendaciones[:limit]
            
        except Exception as e:
            logger.error(f"Error en recomendar_proximos: {str(e)}")
            return []
    
    # =====================================================
    # RECOMENDACIONES HÍBRIDAS
    # =====================================================
    
    async def recomendar_hibridas(
        self,
        lugar_repo,
        usuario_repo,
        usuario_id: str,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        limit: int = 10
    ) -> List[Recomendacion]:
        """
        Recomendaciones híbridas combinando múltiples factores.
        
        Args:
            lugar_repo: Repositorio de lugares
            usuario_repo: Repositorio de usuarios
            usuario_id: ID del usuario
            lat, lng: Ubicación actual (opcional)
            limit: Máximo número de recomendaciones
        
        Returns:
            Lista de recomendaciones combinadas
        """
        try:
            # Obtener favoritos del usuario para excluir
            favoritos = await usuario_repo.get_favoritos(usuario_id, limit=100)
            exclude_ids = [f.get('id') for f in favoritos if f.get('id')]
            
            # Obtener diferentes tipos de recomendaciones
            recs_por_interes = await self.recomendar_por_intereses_usuario(
                usuario_repo, lugar_repo, usuario_id, limit=15, exclude_ids=exclude_ids
            )
            
            recs_populares = await self.recomendar_populares(
                lugar_repo, limit=15, exclude_ids=exclude_ids
            )
            
            recs_tendencias = await self.recomendar_tendencias(
                lugar_repo, limit=10, exclude_ids=exclude_ids
            )
            
            # Combinar y asignar pesos
            todas_recs = {}
            
            for rec in recs_por_interes:
                todas_recs[rec.lugar_id] = {
                    'rec': rec,
                    'puntaje': rec.puntaje * self.pesos['similitud_intereses']
                }
            
            for rec in recs_populares:
                if rec.lugar_id in todas_recs:
                    todas_recs[rec.lugar_id]['puntaje'] += rec.puntaje * self.pesos['popularidad']
                else:
                    todas_recs[rec.lugar_id] = {
                        'rec': rec,
                        'puntaje': rec.puntaje * self.pesos['popularidad']
                    }
            
            for rec in recs_tendencias:
                if rec.lugar_id in todas_recs:
                    todas_recs[rec.lugar_id]['puntaje'] += rec.puntaje * self.pesos['novedad']
                else:
                    todas_recs[rec.lugar_id] = {
                        'rec': rec,
                        'puntaje': rec.puntaje * self.pesos['novedad']
                    }
            
            # Ordenar por puntaje combinado
            resultados = sorted(
                todas_recs.values(),
                key=lambda x: x['puntaje'],
                reverse=True
            )
            
            # Si hay ubicación, reordenar por proximidad (ajuste final)
            if lat is not None and lng is not None:
                from app.services.optimizador_rutas import calcular_distancia_haversine
                
                for item in resultados[:limit]:
                    lugar = await lugar_repo.get_by_id(item['rec'].lugar_id)
                    if lugar:
                        dist = calcular_distancia_haversine(
                            lat, lng,
                            lugar.get('lat', lugar.get('latitud')),
                            lugar.get('lng', lugar.get('longitud'))
                        )
                        item['rec'].distancia_km = round(dist, 2)
                        
                        # Ajustar puntaje por cercanía
                        if dist < 1:
                            item['puntaje'] += 15
                        elif dist < 2:
                            item['puntaje'] += 10
                        elif dist < 5:
                            item['puntaje'] += 5
                
                resultados.sort(key=lambda x: x['puntaje'], reverse=True)
            
            return [item['rec'] for item in resultados[:limit]]
            
        except Exception as e:
            logger.error(f"Error en recomendar_hibridas: {str(e)}")
            return []
    
    # =====================================================
    # FUNCIONES AUXILIARES
    # =====================================================
    
    def _get_interes_nombre(self, interes: str) -> str:
        """Obtener nombre legible del interés."""
        nombres = {
            'cultura': 'cultural',
            'naturaleza': 'natural',
            'gastronomia': 'gastronómico',
            'salsa': 'salsero',
            'aventura': 'de aventura'
        }
        return nombres.get(interes, interes)
    
    def _formatear_distancia(self, distancia_km: float) -> str:
        """Formatear distancia para mostrar."""
        if distancia_km < 0.1:
            return f"{int(distancia_km * 1000)} metros"
        elif distancia_km < 1:
            return f"{int(distancia_km * 1000)} metros"
        else:
            return f"{distancia_km:.1f} kilómetros"
    
    def obtener_tipos_recomendacion(self) -> List[Dict[str, str]]:
        """Obtener lista de tipos de recomendación disponibles."""
        return [
            {"value": TipoRecomendacion.POR_INTERES.value, "label": "Por interés"},
            {"value": TipoRecomendacion.POPULARES.value, "label": "Más populares"},
            {"value": TipoRecomendacion.TENDENCIA.value, "label": "En tendencia"},
            {"value": TipoRecomendacion.SIMILARES.value, "label": "Similares"},
            {"value": TipoRecomendacion.PROXIMOS.value, "label": "Cerca de ti"},
            {"value": TipoRecomendacion.MEJOR_CALIFICADOS.value, "label": "Mejor calificados"},
            {"value": TipoRecomendacion.NUEVOS.value, "label": "Nuevos lugares"}
        ]


# =====================================================
# FUNCIONES DE AYUDA (WRAPPERS)
# =====================================================

async def recomendar_lugares_por_interes(
    lugar_repo,
    interes: str,
    limit: int = 10
) -> List[Recomendacion]:
    """Wrapper rápido para recomendar por interés."""
    service = RecommendationService()
    return await service.recomendar_por_interes(lugar_repo, interes, limit)


async def recomendar_lugares_similares(
    lugar_repo,
    lugar_id: int,
    limit: int = 5
) -> List[Recomendacion]:
    """Wrapper rápido para recomendar lugares similares."""
    service = RecommendationService()
    return await service.recomendar_similares(lugar_repo, lugar_id, limit)


async def get_lugares_populares(
    lugar_repo,
    limit: int = 10
) -> List[Recomendacion]:
    """Wrapper rápido para obtener lugares populares."""
    service = RecommendationService()
    return await service.recomendar_populares(lugar_repo, limit)


async def get_lugares_tendencia(
    lugar_repo,
    limit: int = 10
) -> List[Recomendacion]:
    """Wrapper rápido para obtener lugares en tendencia."""
    service = RecommendationService()
    return await service.recomendar_tendencias(lugar_repo, limit)


# =====================================================
# INSTANCIA GLOBAL
# =====================================================

recommendation_service = RecommendationService()


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Recommendation Service - Prueba de funcionalidad")
    print("=" * 50)
    
    print("\n📋 Tipos de recomendación disponibles:")
    service = RecommendationService()
    for tipo in service.obtener_tipos_recomendacion():
        print(f"   - {tipo['label']} ({tipo['value']})")
    
    print("\n📊 Pesos configurados:")
    for factor, peso in service.pesos.items():
        print(f"   - {factor}: {peso * 100}%")
    
    print("\n✅ RecommendationService inicializado correctamente")
    print("\n💡 Para usar este servicio en producción:")
    print("   1. Conectar con lugar_repo y usuario_repo")
    print("   2. Llamar a recomendar_hibridas() para recomendaciones personalizadas")
    print("   3. Usar recomendar_proximos() para búsquedas por ubicación")