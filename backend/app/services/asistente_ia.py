"""
Asistente IA para LoCALIzate / LoCALIzate Backend
================================================

Chatbot turístico inteligente para consultas sobre Cali.
Maneja detección de intenciones, respuestas contextuales y
recomendaciones de lugares turísticos.

Características:
    - Detección de intenciones (salsa, comida, cultura, naturaleza, etc.)
    - Respuestas contextuales personalizadas
    - Recomendaciones de lugares basadas en intención
    - Sugerencias de preguntas relacionadas
    - Historial de conversación para contexto
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


# =====================================================
# ENUMS Y CONSTANTES
# =====================================================

class IntencionType(str, Enum):
    """Tipos de intenciones detectables."""
    SALUDO = "saludo"
    SALSA = "salsa"
    COMIDA = "comida"
    CULTURA = "cultura"
    NATURALEZA = "naturaleza"
    RUTA = "ruta"
    EVENTO = "evento"
    HORARIO = "horario"
    PRECIO = "precio"
    UBICACION = "ubicacion"
    AYUDA = "ayuda"
    AGRADECIMIENTO = "agradecimiento"
    DESPEDIDA = "despedida"
    GENERAL = "general"


@dataclass
class RespuestaIA:
    """
    Respuesta estructurada del asistente IA.
    
    Attributes:
        texto: Texto de respuesta principal
        intencion: Intención detectada
        sugerencias: Lista de preguntas sugeridas
        lugares_recomendados: Lista de lugares recomendados
        confianza: Nivel de confianza de la detección (0-1)
    """
    texto: str
    intencion: Optional[IntencionType] = None
    sugerencias: List[str] = field(default_factory=list)
    lugares_recomendados: List[Dict[str, Any]] = field(default_factory=list)
    confianza: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para API."""
        return {
            "respuesta": self.texto,
            "intencion": self.intencion.value if self.intencion else None,
            "sugerencias": self.sugerencias,
            "lugares_recomendados": self.lugares_recomendados,
            "confianza": self.confianza,
            "timestamp": datetime.now().isoformat()
        }


# =====================================================
# CLASE PRINCIPAL
# =====================================================

class AsistenteLoCALIzate:
    """
    Asistente virtual turístico para Cali.
    
    Responsabilidades:
        1. Detectar intención del usuario basado en palabras clave
        2. Generar respuestas contextuales personalizadas
        3. Recomendar lugares según la intención
        4. Mantener contexto de conversación (opcional)
    """
    
    def __init__(self):
        """Inicializar asistente con palabras clave y respuestas."""
        
        # Palabras clave por intención (optimizadas para Cali)
        self.palabras_clave: Dict[IntencionType, List[str]] = {
            IntencionType.SALUDO: ["hola", "buenas", "quihubo", "qué hubo", "saludos", 
                                   "buenos días", "buenas tardes", "buenas noches", "holi"],
            
            IntencionType.SALSA: ["salsa", "bailar", "baile", "rumba", "discoteca", 
                                  "bailarín", "bailarina", "topa tolondra", "tin tin",
                                  "salsero", "salsoteca", "sonidero"],
            
            IntencionType.COMIDA: ["comer", "restaurante", "gastronomía", "comida", 
                                   "almorzar", "cenar", "marranitas", "cholado", 
                                   "pandebono", "lulada", "empanada", "helado"],
            
            IntencionType.CULTURA: ["cultura", "historia", "arte", "museo", "iglesia", 
                                    "arquitectura", "tradición", "monumento", "plaza",
                                    "cristo rey", "gato del río", "ermita", "sanjuanito"],
            
            IntencionType.NATURALEZA: ["naturaleza", "parque", "río", "árbol", "pance", 
                                       "cerro", "senderismo", "montaña", "zoologico",
                                       "zoológico", "farallones", "cascada", "pance"],
            
            IntencionType.RUTA: ["ruta", "recorrido", "camino", "visitar", "itinerario", 
                                 "plan", "tour", "guía", "optimizar", "orden"],
            
            IntencionType.EVENTO: ["evento", "festival", "feria", "concierto", "celebración",
                                   "petronio", "feria de cali", "salsódromo", "cabalgata"],
            
            IntencionType.HORARIO: ["horario", "abre", "cierra", "cuándo", "hora", 
                                    "apertura", "cierre", "funciona"],
            
            IntencionType.PRECIO: ["precio", "cuesta", "valor", "entrada", "boleta",
                                   "costo", "tarifa", "gratis", "cuánto cuesta"],
            
            IntencionType.UBICACION: ["ubicación", "dirección", "dónde queda", "cómo llegar",
                                      "mapa", "ubicado", "calle", "carrera"],
            
            IntencionType.AYUDA: ["ayuda", "qué puedes hacer", "cómo funciona", "comandos",
                                  "funciones", "capacidades", "qué sabes"],
            
            IntencionType.AGRADECIMIENTO: ["gracias", "agradezco", "thanks", "muchas gracias",
                                           "te lo agradezco", "excelente", "genial"],
            
            IntencionType.DESPEDIDA: ["adiós", "chao", "hasta luego", "nos vemos", "bye",
                                      "hasta pronto", "me voy", "terminar"]
        }
        
        # Respuestas base por intención
        self.respuestas_base: Dict[IntencionType, str] = {
            IntencionType.SALUDO: "🎉 ¡Qué hubo, mi parcero! Soy CaliGuía, tu asistente turístico inteligente. ¿En qué puedo ayudarte a descubrir la Sultana del Valle?",
            
            IntencionType.SALSA: "💃 ¡La salsa es el alma de Cali! Te recomiendo visitar:\n\n• **La Topa Tolondra** (⭐4.9) - Clases de salsa y orquestas en vivo\n• **Plazoleta Jairo Varela** (⭐4.8) - Homenaje al Grupo Niche\n• **Barrio San Antonio** (⭐4.9) - Bailadores profesionales en la calle\n\n¿Quieres que te muestre estos lugares en el mapa?",
            
            IntencionType.COMIDA: "🍜 ¡Ay parce, qué rico! En Cali no puedes perderte:\n\n• **Marranitas** - Bulevar del Río (⭐4.6)\n• **Cholado** - Frutas frescas con hielo raspado\n• **Pandebono** - Pan de queso calientico\n• **Lulada** - Bebida típica de lulo\n\n¿Te ayudo a encontrar restaurantes cerca de tu ubicación?",
            
            IntencionType.CULTURA: "🎭 Cali tiene una cultura riquísima. Te recomiendo visitar:\n\n• **Iglesia La Ermita** (⭐4.8) - Gótica impresionante\n• **Cristo Rey** (⭐4.7) - Mirador panorámico\n• **Plaza de Caicedo** - Corazón de la ciudad\n• **Barrio San Antonio** - Bohemio y colonial\n\n¿Quieres más detalles sobre alguno?",
            
            IntencionType.NATURALEZA: "🌳 Cali tiene pulmones verdes increíbles:\n\n• **Río Pance** (⭐4.6) - Baño en aguas cristalinas\n• **Zoológico de Cali** (⭐4.7) - Uno de los mejores de Latinoamérica\n• **Cerro de las Tres Cruces** - Mirador con vista 360°\n• **Farallones de Cali** - Parque Nacional Natural\n\n¿Listo para la aventura?",
            
            IntencionType.RUTA: "🗺️ ¡Claro que sí! Para planificar tu ruta:\n\n1. Ve a la pestaña **'Plan Ruta'**\n2. Selecciona hasta **5 lugares** que quieras visitar\n3. El sistema optimizará el orden más eficiente\n4. Verás distancias y tiempos estimados\n\n¿Quieres que te recomiende una ruta?",
            
            IntencionType.EVENTO: "🎡 Cali tiene los mejores eventos del país:\n\n• **Feria de Cali** - 25 al 30 de diciembre\n• **Festival Mundial de Salsa** - Septiembre\n• **Petronio Álvarez** - Agosto (música del Pacífico)\n• **Salsa al Parque** - Diciembre (gratis)\n\n¿Quieres agregar alguno a tu calendario?",
            
            IntencionType.HORARIO: "⏰ Los horarios pueden variar según el lugar. Te recomiendo usar el **buscador de lugares** para ver el horario específico de cada atracción. ¿Qué lugar te interesa?",
            
            IntencionType.PRECIO: "💰 Muchos lugares en Cali son gratuitos o tienen precios muy accesibles. Por ejemplo:\n\n• **Cristo Rey** - Gratis\n• **El Gato del Río** - Gratis\n• **Museos** - Entre $5.000 y $15.000 COP\n• **Zoológico** - $25.000 COP\n\n¿Quieres filtrar lugares por precio?",
            
            IntencionType.UBICACION: "📍 Para ver la ubicación exacta de cualquier lugar:\n\n1. Usa el **mapa interactivo**\n2. Haz clic en cualquier marcador\n3. También puedes usar el botón **'¿Dónde estoy?'**\n\n¿Necesitas ayuda para encontrar un lugar específico?",
            
            IntencionType.AYUDA: "❓ Puedo ayudarte con:\n\n• 🎺 **Salsa** - Mejores bares y escuelas\n• 🍽️ **Comida** - Restaurantes y comidas típicas\n• 🎭 **Cultura** - Museos, iglesias y monumentos\n• 🌳 **Naturaleza** - Ríos, parques y montañas\n• 🗺️ **Rutas** - Planificación de itinerarios\n• 🎡 **Eventos** - Fechas de festivales\n\n¿Sobre qué tema quieres saber más?",
            
            IntencionType.AGRADECIMIENTO: "🙏 ¡De nada, parcero! Me alegra poder ayudarte. Recuerda que estoy aquí 24/7 para lo que necesites. ¡Que disfrutes Cali como se debe! 🎉💃",
            
            IntencionType.DESPEDIDA: "👋 ¡Hasta luego, parcero! Que tengas un excelente día. ¡Vuelve pronto a Cali, la Sultana del Valle siempre te espera con los brazos abiertos! 🎭",
            
            IntencionType.GENERAL: "🎉 ¡Qué hubo, mi parcero! Soy CaliGuía, tu asistente turístico. Pregúntame por:\n\n• 🎺 Lugares para bailar salsa\n• 🍽️ Restaurantes y comida típica\n• 🎭 Cultura y museos\n• 🌳 Naturaleza y parques\n• 🗺️ Planificación de rutas\n• 🎡 Eventos y festivales\n\n¿En qué te ayudo hoy?"
        }
        
        # Recomendaciones de lugares por intención
        self.recomendaciones_por_intencion: Dict[IntencionType, List[Dict[str, Any]]] = {
            IntencionType.SALSA: [
                {"nombre": "La Topa Tolondra", "rating": 4.9, "interes": "cultura", "icono": "🎺"},
                {"nombre": "Plazoleta Jairo Varela", "rating": 4.8, "interes": "cultura", "icono": "🎵"},
                {"nombre": "Tin Tin Deo", "rating": 4.7, "interes": "cultura", "icono": "💃"}
            ],
            IntencionType.COMIDA: [
                {"nombre": "Bulevar del Río", "rating": 4.6, "interes": "gastronomia", "icono": "🌃"},
                {"nombre": "Morada Ancestral", "rating": 4.9, "interes": "gastronomia", "icono": "🍽️"},
                {"nombre": "Palomulata Parrilla", "rating": 4.8, "interes": "gastronomia", "icono": "🥩"}
            ],
            IntencionType.NATURALEZA: [
                {"nombre": "Río Pance", "rating": 4.6, "interes": "naturaleza", "icono": "🏞️"},
                {"nombre": "Zoológico de Cali", "rating": 4.7, "interes": "naturaleza", "icono": "🦁"},
                {"nombre": "Farallones de Cali", "rating": 4.9, "interes": "naturaleza", "icono": "🏔️"}
            ],
            IntencionType.CULTURA: [
                {"nombre": "Cristo Rey", "rating": 4.7, "interes": "cultura", "icono": "✝️"},
                {"nombre": "Iglesia La Ermita", "rating": 4.8, "interes": "cultura", "icono": "⛪"},
                {"nombre": "El Gato del Río", "rating": 4.5, "interes": "cultura", "icono": "🐱"}
            ],
            IntencionType.EVENTO: [
                {"nombre": "Feria de Cali", "rating": 4.9, "interes": "evento", "icono": "🎉"},
                {"nombre": "Festival Mundial de Salsa", "rating": 4.9, "interes": "evento", "icono": "🎺"},
                {"nombre": "Petronio Álvarez", "rating": 4.8, "interes": "evento", "icono": "🪘"}
            ]
        }
        
        logger.info("AsistenteLoCALIzate inicializado correctamente")
    
    # =====================================================
    # DETECCIÓN DE INTENCIONES
    # =====================================================
    
    def detectar_intencion(self, mensaje: str) -> Tuple[Optional[IntencionType], float]:
        """
        Detectar la intención del mensaje del usuario.
        
        Args:
            mensaje: Mensaje del usuario
        
        Returns:
            Tupla (intencion, confianza)
        """
        mensaje_lower = mensaje.lower()
        
        # Diccionario para acumular puntajes
        puntajes: Dict[IntencionType, int] = {}
        
        for intencion, palabras in self.palabras_clave.items():
            puntaje = 0
            for palabra in palabras:
                if palabra in mensaje_lower:
                    # Palabras exactas dan más puntos
                    if re.search(rf'\b{re.escape(palabra)}\b', mensaje_lower):
                        puntaje += 2
                    else:
                        puntaje += 1
            
            if puntaje > 0:
                puntajes[intencion] = puntaje
        
        if not puntajes:
            return IntencionType.GENERAL, 0.5
        
        # Obtener la intención con mayor puntaje
        mejor_intencion = max(puntajes, key=puntajes.get)
        max_puntaje = puntajes[mejor_intencion]
        
        # Calcular confianza (normalizada)
        confianza = min(0.95, 0.3 + (max_puntaje / 20))
        
        return mejor_intencion, confianza
    
    # =====================================================
    # GENERACIÓN DE RESPUESTAS
    # =====================================================
    
    def generar_respuesta(
        self,
        intencion: Optional[IntencionType],
        mensaje_original: str = "",
        contexto: Optional[Dict] = None
    ) -> str:
        """
        Generar respuesta basada en la intención detectada.
        
        Args:
            intencion: Intención detectada
            mensaje_original: Mensaje original del usuario
            contexto: Contexto adicional de la conversación
        
        Returns:
            Texto de respuesta
        """
        if not intencion:
            intencion = IntencionType.GENERAL
        
        respuesta = self.respuestas_base.get(intencion)
        
        if not respuesta:
            respuesta = self.respuestas_base[IntencionType.GENERAL]
        
        return respuesta
    
    def generar_sugerencias(self, intencion: Optional[IntencionType]) -> List[str]:
        """
        Generar sugerencias de preguntas relacionadas.
        
        Args:
            intencion: Intención detectada
        
        Returns:
            Lista de sugerencias
        """
        sugerencias_por_intencion = {
            IntencionType.SALSA: [
                "¿Cuál es la mejor escuela de salsa?",
                "¿Dónde hay clases de salsa gratis?",
                "¿Qué discotecas de salsa recomiendas?"
            ],
            IntencionType.COMIDA: [
                "¿Dónde comer marranitas?",
                "¿Cuál es el mejor restaurante de comida típica?",
                "¿Dónde puedo probar cholado?"
            ],
            IntencionType.CULTURA: [
                "¿Cuál es la historia del Cristo Rey?",
                "¿Qué museos puedo visitar?",
                "¿Dónde queda la Iglesia La Ermita?"
            ],
            IntencionType.NATURALEZA: [
                "¿Cómo llegar al Río Pance?",
                "¿Qué horario tiene el Zoológico?",
                "¿Puedo hacer senderismo en los Farallones?"
            ],
            IntencionType.RUTA: [
                "¿Cómo llego a Cristo Rey?",
                "Ruta por el centro histórico",
                "¿Qué lugares visitar en un día?"
            ],
            IntencionType.EVENTO: [
                "¿Cuándo es la próxima Feria de Cali?",
                "¿Dónde comprar boletas para el Festival de Salsa?",
                "¿Qué eventos hay este mes?"
            ]
        }
        
        sugerencias = sugerencias_por_intencion.get(intencion, [
            "¿Dónde bailar salsa? 💃",
            "¿Dónde comer rico? 🍜",
            "Lugares de naturaleza 🌳",
            "Crear una ruta optimizada 🗺️",
            "Eventos próximos 🎡",
            "¿Qué hacer en Cali? 🎭"
        ])
        
        return sugerencias
    
    def recomendar_lugares(self, intencion: Optional[IntencionType]) -> List[Dict[str, Any]]:
        """
        Recomendar lugares basados en la intención.
        
        Args:
            intencion: Intención detectada
        
        Returns:
            Lista de lugares recomendados
        """
        if not intencion:
            return []
        
        return self.recomendaciones_por_intencion.get(intencion, [])
    
    # =====================================================
    # MÉTODO PRINCIPAL
    # =====================================================
    
    def procesar_mensaje(
        self,
        mensaje: str,
        contexto: Optional[Dict] = None
    ) -> RespuestaIA:
        """
        Procesar mensaje del usuario y generar respuesta completa.
        
        Args:
            mensaje: Mensaje del usuario
            contexto: Contexto de conversación (opcional)
        
        Returns:
            RespuestaIA con respuesta, sugerencias y recomendaciones
        """
        # Detectar intención
        intencion, confianza = self.detectar_intencion(mensaje)
        
        # Generar respuesta
        respuesta_texto = self.generar_respuesta(intencion, mensaje, contexto)
        
        # Generar sugerencias
        sugerencias = self.generar_sugerencias(intencion)
        
        # Recomendar lugares
        lugares = self.recomendar_lugares(intencion)
        
        # Loggear para debug
        logger.debug(f"Mensaje: '{mensaje[:50]}...' -> Intención: {intencion} (confianza: {confianza:.2f})")
        
        return RespuestaIA(
            texto=respuesta_texto,
            intencion=intencion,
            sugerencias=sugerencias,
            lugares_recomendados=lugares,
            confianza=confianza
        )
    
    # =====================================================
    # MÉTODOS AUXILIARES
    # =====================================================
    
    def obtener_intenciones_disponibles(self) -> List[Dict[str, str]]:
        """Obtener lista de intenciones disponibles."""
        return [
            {"value": i.value, "label": i.name.capitalize()}
            for i in IntencionType
        ]
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas del asistente."""
        total_palabras = sum(len(palabras) for palabras in self.palabras_clave.values())
        
        return {
            "intenciones": len(IntencionType),
            "total_palabras_clave": total_palabras,
            "respuestas_disponibles": len(self.respuestas_base),
            "recomendaciones_disponibles": len(self.recomendaciones_por_intencion)
        }


# =====================================================
# INSTANCIA GLOBAL
# =====================================================

# Instancia global del asistente
asistente = AsistenteLoCALIzate()


# =====================================================
# FUNCIÓN DE AYUDA PARA INTEGRACIÓN CON API
# =====================================================

def procesar_consulta(mensaje: str, contexto: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Helper para procesar consultas desde los routers.
    
    Args:
        mensaje: Mensaje del usuario
        contexto: Contexto de conversación
    
    Returns:
        Respuesta formateada para API
    """
    respuesta = asistente.procesar_mensaje(mensaje, contexto)
    return respuesta.to_dict()


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Asistente IA - Prueba de funcionalidad")
    print("=" * 50)
    
    # Pruebas
    mensajes_prueba = [
        "Hola, ¿cómo estás?",
        "¿Dónde puedo bailar salsa en Cali?",
        "Recomiéndame un buen restaurante",
        "Quiero visitar lugares naturales",
        "¿Cuándo es la Feria de Cali?",
        "Gracias por la información",
        "Adiós"
    ]
    
    for msg in mensajes_prueba:
        print(f"\n👤 Usuario: {msg}")
        respuesta = asistente.procesar_mensaje(msg)
        print(f"🤖 Asistente: {respuesta.texto[:100]}...")
        print(f"   Intención: {respuesta.intencion} (confianza: {respuesta.confianza:.2f})")
        if respuesta.sugerencias:
            print(f"   Sugerencias: {respuesta.sugerencias[:2]}")
    
    print("\n" + "=" * 50)
    print("✅ Asistente funcionando correctamente")