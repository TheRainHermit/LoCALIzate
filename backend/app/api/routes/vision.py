# backend/app/api/routes/vision.py

from fastapi import APIRouter, File, UploadFile, HTTPException
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

router = APIRouter()

# Lazy imports: solo importar cuando sea necesario para evitar errores de startup


@router.post("/detect")
async def detect_monument(file: UploadFile = File(...)):
    """
    Recibe una foto → Identifica monumento → Retorna info enriquecida
    """
    try:
        # Import lazy (solo cuando se necesita)
        from app.ml.vision_models.monument_detector import MonumentDetector
        from app.services.vision_service import VisionService
        from PIL import Image

        # Leer imagen
        contents = await file.read()
        image = Image.open(BytesIO(contents))

        # Detectar monumento
        detector = MonumentDetector()
        predictions = detector.predict(image)

        if not predictions or predictions[0].get("confidence", 0) < 0.6:
            return {
                "success": False,
                "message": "No pude identificar lo que estás mirando. ¿Intentas nuevamente?",
                "confidence": 0,
            }

        top_prediction = predictions[0]
        monument_name = top_prediction.get("class")
        confidence = top_prediction.get("confidence", 0)

        # Buscar lugar en DB
        vision_service = VisionService()
        lugar = await vision_service.find_lugar_by_name(monument_name)

        if not lugar:
            return {
                "success": False,
                "message": "Interesante, pero aún no tengo info de esto",
            }

        # Obtener audio guía
        audio = await vision_service.get_audio_guide(lugar.get("id"))

        return {
            "success": True,
            "lugar": lugar,
            "confidence": confidence,
            "audio_guia": audio,
            "mensaje_caleño": f"¡Oís! {lugar.get('tip_caleño', '')}",
        }

    except Exception as e:
        logger.error(f"Error en detect_monument: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/identify")
async def identify_monument(base64_image: str):
    """
    Versión alternativa: recibe imagen en base64
    """
    try:
        from app.ml.vision_models.monument_detector import MonumentDetector
        from app.services.vision_service import VisionService
        from PIL import Image
        import base64

        # Decodificar base64
        image_data = base64.b64decode(base64_image)
        image = Image.open(BytesIO(image_data))

        detector = MonumentDetector()
        predictions = detector.predict(image)

        if not predictions:
            return {"success": False, "message": "No se identificó nada"}

        return {
            "success": True,
            "predictions": predictions,
        }

    except Exception as e:
        logger.error(f"Error en identify_monument: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))