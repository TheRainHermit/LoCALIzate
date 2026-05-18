# backend/app/api/routes/vision.py

from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.vision_service import VisionService
from app.ml.vision_models.monument_detector import MonumentDetector
from app.services.recomendacion_service import RecommendationService
import base64
from io import BytesIO
from PIL import Image

router = APIRouter()
vision_service = VisionService()
detector = MonumentDetector()
recommender = RecommendationService()

@router.post("/detect")
async def detect_monument(file: UploadFile = File(...)):
    """
    Recibe una foto → Identifica monumento → Retorna info enriquecida
    
    Flow:
    1. Recibir imagen base64
    2. Preprocesar con TensorFlow Lite
    3. Inferir contra modelo de monumentos
    4. Buscar en DB el lugar con mayor confianza
    5. Retornar lugar + audio-guía + recomendaciones
    """
    try:
        # Leer imagen
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        
        # Detectar monumento con confianza
        predictions = detector.predict(image)
        
        if not predictions or predictions[0]['confidence'] < 0.6:
            return {
                "success": False,
                "message": "No pude identificar lo que estás mirando. ¿Intentas nuevamente?",
                "confidence": 0
            }
        
        top_prediction = predictions[0]  # Mayor confianza
        monument_name = top_prediction['class']
        confidence = top_prediction['confidence']
        
        # Buscar lugar en DB
        lugar = await vision_service.find_lugar_by_name(monument_name)
        
        if not lugar:
            return {
                "success": False,
                "message": "Interesante, pero aún no tengo info de esto"
            }
        
        # Obtener audio guía
        audio = await vision_service.get_audio_guide(lugar['id'])
        
        # Obtener recomendaciones cerca
        recomendaciones = await recommender.get_nearby_recommendations(
            lat=lugar['lat'],
            lng=lugar['lng'],
            radius_km=2
        )
        
        return {
            "success": True,
            "lugar": lugar,
            "confidence": confidence,
            "audio_guia": audio,
            "recomendaciones": recomendaciones,
            "mensaje_caleño": f"¡Oís! {lugar['tip_caleño']}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))