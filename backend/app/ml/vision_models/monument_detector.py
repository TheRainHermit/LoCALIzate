# backend/app/ml/vision_models/monument_detector.py

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class MonumentDetector:
    """
    Detector de monumentos usando modelos de ML.
    En producción: TensorFlow Lite con modelo entrenado.
    """

    def __init__(self, model_path: str = None):
        """Inicializar detector (stub por ahora)"""
        logger.info("Inicializando MonumentDetector...")
        self.model_path = model_path
        # TODO: Cargar modelo TensorFlow Lite en producción

    def predict(self, image) -> List[Dict[str, Any]]:
        """
        Predecir monumentos en una imagen

        Args:
            image: PIL Image object

        Returns:
            List de predicciones con formato:
            [
                {
                    'class': 'Cristo Rey',
                    'confidence': 0.95,
                    'bbox': [x1, y1, x2, y2]
                },
                ...
            ]
        """
        logger.info("Prediciendo monumentos en imagen...")
        # Stub: retornar predicción vacía por ahora
        return []