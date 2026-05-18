# backend/app/services/recomendacion_service.py

from supabase import create_client
from app.config import settings
from typing import List
import math

class RecommendationService:
    def __init__(self):
        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    async def get_recommendations(
        self,
        user_id: int,
        user_lat: float,
        user_lng: float,
        radius_km: float = 3.0
    ) -> List[dict]:
        """
        Algoritmo de recomendaciones personalizado:
        
        1. Obtener perfil usuario (intereses)
        2. Buscar lugares con categorías que coincidan
        3. Filtrar por distancia (GPS)
        4. Ordenar por rating + noveledad
        5. Evitar duplicados (ya visitados)
        """
        
        # 1. Obtener usuario
        user = self.supabase.table('usuarios').select('*').eq('id', user_id).single().execute()
        intereses = user.data.get('intereses', [])
        
        # 2. Buscar lugares con categorías coincidentes
        # SQL generado dinámicamente
        query = self.supabase.table('lugares').select('*')
        
        # Filtrar por categorías (OVERLAPS = intersección de arrays)
        query = query.or_filter(f"categorias.cs.{{{','.join(intereses)}}}")
        
        # 3. Filtrar por distancia (Haversine formula)
        lugares = query.execute().data
        
        lugares_filtrados = []
        for lugar in lugares:
            distance = self._haversine_distance(
                user_lat, user_lng,
                lugar['lat'], lugar['lng']
            )
            
            if distance <= radius_km:
                # Agregar score de relevancia
                score = self._calculate_score(
                    distance=distance,
                    rating=lugar['rating_promedio'],
                    visitas=lugar['visitas_mensuales'],
                    match_categories=self._count_matching_categories(
                        lugar['categorias'],
                        intereses
                    )
                )
                
                lugar['score'] = score
                lugar['distance_km'] = distance
                lugares_filtrados.append(lugar)
        
        # 4. Ordenar por score descendente
        lugares_filtrados.sort(key=lambda x: x['score'], reverse=True)
        
        # 5. Limitar a top 5 recomendaciones
        return lugares_filtrados[:5]
    
    def _haversine_distance(self, lat1, lng1, lat2, lng2) -> float:
        """Calcula distancia en km entre dos puntos GPS"""
        R = 6371  # Radio de la Tierra en km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _calculate_score(self, distance, rating, visitas, match_categories) -> float:
        """
        Scoring: combina múltiples factores
        - Cercanía (más cercano = más puntos)
        - Rating (lugares bien evaluados)
        - Popularidad (muchas visitas)
        - Relevancia (coincide con intereses)
        """
        
        # Normalizar distancia (0 a 1, donde 1 = muy cercano)
        proximity_score = max(0, 1 - (distance / 3.0))
        
        # Rating normalizado (0 a 1)
        rating_score = rating / 5.0
        
        # Popularidad normalizada
        popularity_score = min(1, visitas / 5000)
        
        # Relevancia
        relevance_score = min(1, match_categories / 3)
        
        # Peso combinado
        total_score = (
            proximity_score * 0.3 +
            rating_score * 0.2 +
            popularity_score * 0.2 +
            relevance_score * 0.3
        )
        
        return total_score
    
    def _count_matching_categories(self, lugar_cats, user_interests) -> int:
        """Cuenta cuántas categorías del lugar coinciden con intereses"""
        return len(set(lugar_cats) & set(user_interests))