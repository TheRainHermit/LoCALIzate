"""
Chat Schemas for LoCALIzate Backend
==================================

Pydantic models for chat and AI assistant request/response validation.

Schemas:
    - MensajeBase: Base fields for message
    - MensajeRequest: Message request
    - MensajeResponse: Message response
    - ChatRequest: Chat API request
    - ChatResponse: Chat API response
    - ConversacionResponse: Conversation summary response
    - ConversacionDetailResponse: Conversation with messages
    - MensajeHistorialResponse: Message in history
    - SugerenciaResponse: Suggested questions
    - RolMensaje: Message role enum
    - IntencionType: Intent detection enum
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


# =====================================================
# ENUMS
# =====================================================

class RolMensaje(str, Enum):
    """Role of the message sender."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    
    @classmethod
    def list_values(cls) -> List[str]:
        return [item.value for item in cls]
    
    @classmethod
    def get_display_name(cls, value: str) -> str:
        names = {"user": "Usuario", "assistant": "Asistente", "system": "Sistema"}
        return names.get(value, value)
    
    @classmethod
    def get_icon(cls, value: str) -> str:
        icons = {"user": "👤", "assistant": "🤖", "system": "⚙️"}
        return icons.get(value, "💬")


class IntencionType(str, Enum):
    """User intent types for better response handling."""
    SALUDO = "saludo"
    SALSA = "salsa"
    GASTRONOMIA = "gastronomia"
    NATURALEZA = "naturaleza"
    CULTURA = "cultura"
    EVENTOS = "eventos"
    RUTAS = "rutas"
    LUGARES = "lugares"
    HORARIOS = "horarios"
    PRECIOS = "precios"
    UBICACION = "ubicacion"
    AYUDA = "ayuda"
    AGRADECIMIENTO = "agradecimiento"
    DESPEDIDA = "despedida"
    GENERAL = "general"
    
    @classmethod
    def list_values(cls) -> List[str]:
        return [item.value for item in cls]
    
    @classmethod
    def get_display_name(cls, value: str) -> str:
        names = {
            "saludo": "👋 Saludo",
            "salsa": "💃 Salsa",
            "gastronomia": "🍽️ Gastronomía",
            "naturaleza": "🌳 Naturaleza",
            "cultura": "🎭 Cultura",
            "eventos": "📅 Eventos",
            "rutas": "🗺️ Rutas",
            "lugares": "📍 Lugares",
            "horarios": "⏰ Horarios",
            "precios": "💰 Precios",
            "ubicacion": "📍 Ubicación",
            "ayuda": "❓ Ayuda",
            "agradecimiento": "🙏 Agradecimiento",
            "despedida": "👋 Despedida",
            "general": "💬 General"
        }
        return names.get(value, value)


# =====================================================
# BASE SCHEMAS
# =====================================================

class MensajeBase(BaseModel):
    """Base schema for message."""
    
    contenido: str = Field(..., min_length=1, max_length=2000, description="Contenido del mensaje")
    intencion: Optional[IntencionType] = Field(None, description="Intención detectada")
    lugares_referenciados: Optional[List[int]] = Field(None, description="IDs de lugares mencionados")
    
    @field_validator("contenido")
    @classmethod
    def validate_contenido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El mensaje no puede estar vacío")
        return v


class MensajeRequest(BaseModel):
    """Request schema for sending a message."""
    
    mensaje: str = Field(..., min_length=1, max_length=2000, description="Mensaje del usuario")
    conversacion_id: Optional[int] = Field(None, description="ID de conversación existente")
    user_lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitud actual del usuario")
    user_lng: Optional[float] = Field(None, ge=-180, le=180, description="Longitud actual del usuario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mensaje": "¿Dónde puedo bailar salsa en Cali?",
                "conversacion_id": None,
                "user_lat": 3.4516,
                "user_lng": -76.5320
            }
        }
    )
    
    @field_validator("mensaje")
    @classmethod
    def validate_mensaje(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El mensaje no puede estar vacío")
        return v


class MensajeResponse(BaseModel):
    """Response schema for a message."""
    
    id: int
    conversacion_id: int
    rol: str
    contenido: str
    intencion: Optional[str]
    created_at: str
    
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# CHAT API SCHEMAS
# =====================================================

class LugarRecomendadoResponse(BaseModel):
    """Recommended place in chat response."""
    
    id: int
    nombre: str
    rating: float
    interes: str
    icono: str
    distancia_km: Optional[float] = None


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    
    mensaje: str = Field(..., min_length=1, max_length=2000, description="Mensaje del usuario")
    conversacion_id: Optional[int] = Field(None, description="ID de conversación existente")
    user_lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitud actual")
    user_lng: Optional[float] = Field(None, ge=-180, le=180, description="Longitud actual")
    
    @property
    def tiene_ubicacion(self) -> bool:
        return self.user_lat is not None and self.user_lng is not None


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    
    respuesta: str = Field(..., description="Respuesta del asistente")
    conversacion_id: int = Field(..., description="ID de la conversación")
    mensaje_id: int = Field(..., description="ID del mensaje del asistente")
    intencion: Optional[str] = Field(None, description="Intención detectada")
    sugerencias: List[str] = Field(default_factory=list, description="Sugerencias de preguntas")
    lugares_recomendados: List[LugarRecomendadoResponse] = Field(default_factory=list)
    confianza: float = Field(default=0.0, description="Confianza de la detección")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# =====================================================
# CONVERSATION SCHEMAS
# =====================================================

class ConversacionResponse(BaseModel):
    """Response schema for conversation summary."""
    
    id: int
    titulo: str
    created_at: str
    updated_at: str
    mensaje_count: int
    ultimo_mensaje: Optional[str] = None
    ultimo_mensaje_fecha: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class MensajeHistorialResponse(BaseModel):
    """Response schema for message in history."""
    
    id: int
    rol: str
    contenido: str
    intencion: Optional[str] = None
    created_at: str
    
    model_config = ConfigDict(from_attributes=True)


class ConversacionDetailResponse(BaseModel):
    """Response schema for conversation with messages."""
    
    id: int
    titulo: str
    usuario_id: str
    created_at: str
    updated_at: str
    mensajes: List[MensajeHistorialResponse] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# SUGGESTIONS SCHEMA
# =====================================================

class SugerenciaResponse(BaseModel):
    """Response schema for suggested questions."""
    
    preguntas: List[str] = Field(..., description="Lista de preguntas sugeridas")
    categoria: Optional[str] = Field(None, description="Categoría de las sugerencias")


# =====================================================
# INTENT DETECTION SCHEMA
# =====================================================

class IntentDetectionResult(BaseModel):
    """Result of intent detection."""
    
    intencion: IntencionType
    confianza: float = Field(..., ge=0, le=1, description="Confianza de detección (0-1)")
    palabras_clave: List[str] = Field(default_factory=list)
    entidades: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def confianza_porcentaje(self) -> int:
        return int(self.confianza * 100)


# =====================================================
# MESSAGE TEMPLATE SCHEMA
# =====================================================

class MessageTemplate(BaseModel):
    """Template for assistant responses."""
    
    intencion: IntencionType
    template: str
    requires_context: bool = False
    examples: List[str] = Field(default_factory=list)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_intenciones_disponibles() -> List[Dict[str, str]]:
    """Get list of available intents with display info."""
    return [
        {
            "value": intent.value,
            "label": intent.get_display_name(intent.value)
        }
        for intent in IntencionType
    ]


def get_roles_mensaje() -> List[Dict[str, str]]:
    """Get list of message roles with display info."""
    return [
        {
            "value": role.value,
            "label": role.get_display_name(role.value),
            "icon": role.get_icon(role.value)
        }
        for role in RolMensaje
    ]


# Predefined message templates
MESSAGE_TEMPLATES = [
    MessageTemplate(
        intencion=IntencionType.SALUDO,
        template="¡Qué hubo, parcero! 🎭 Soy tu asistente turístico de Cali. ¿En qué puedo ayudarte hoy?",
        examples=["Hola", "Buenos días", "Qué hubo"]
    ),
    MessageTemplate(
        intencion=IntencionType.SALSA,
        template="¡La salsa es el alma de Cali! 🎺 Te recomiendo visitar La Topa Tolondra, Tin Tin Deo o la Plazoleta Jairo Varela.",
        examples=["dónde bailar salsa", "mejores bares de salsa"]
    ),
    MessageTemplate(
        intencion=IntencionType.GASTRONOMIA,
        template="Cali es un paraíso gastronómico 🍽️. Prueba Morada Ancestral, Palomulata Parrilla o el Tour Gastronómico del Pacífico.",
        examples=["restaurantes", "comida típica", "dónde comer"]
    ),
    MessageTemplate(
        intencion=IntencionType.NATURALEZA,
        template="Para conectar con la naturaleza 🌳 te recomiendo el Río Pance, los Farallones de Cali o el Zoológico de Cali.",
        examples=["parques", "ríos", "montañas", "senderismo"]
    ),
    MessageTemplate(
        intencion=IntencionType.CULTURA,
        template="Descubre la cultura caleña 🎭 visitando el Cristo Rey, la Iglesia La Ermita o el Museo del Oro Calima.",
        examples=["museos", "historia", "iglesias"]
    ),
    MessageTemplate(
        intencion=IntencionType.EVENTOS,
        template="Los eventos más importantes de Cali 📅: Feria de Cali (25-30 Dic), Festival Mundial de Salsa (24-28 Sep).",
        examples=["feria", "festivales", "conciertos"]
    ),
    MessageTemplate(
        intencion=IntencionType.RUTAS,
        template="¡Perfecto! 🗺️ Usa el planificador de rutas. Selecciona hasta 5 lugares y te optimizo la ruta más corta.",
        examples=["planificar ruta", "itinerario", "recorrido"]
    ),
    MessageTemplate(
        intencion=IntencionType.AGRADECIMIENTO,
        template="¡De nada, parcero! 🤙 Disfruta tu viaje por la Sultana del Valle. ¡Que viva la salsa! 🎺💃",
        examples=["gracias", "muchas gracias", "thank you"]
    ),
    MessageTemplate(
        intencion=IntencionType.DESPEDIDA,
        template="¡Hasta luego, parcero! 🎭 Que tengas un excelente día. ¡Vuelve pronto a Cali!",
        examples=["adiós", "chao", "hasta luego"]
    ),
    MessageTemplate(
        intencion=IntencionType.AYUDA,
        template="Puedo ayudarte con información sobre 🎺 salsa, 🍽️ restaurantes, 🌳 naturaleza, 🎭 cultura, 📅 eventos y 🗺️ rutas.",
        examples=["ayuda", "qué puedes hacer", "comandos"]
    )
]


def get_template_by_intent(intencion: IntencionType) -> Optional[MessageTemplate]:
    """Get message template by intent."""
    for template in MESSAGE_TEMPLATES:
        if template.intencion == intencion:
            return template
    return None


def detectar_intencion_ejemplo(mensaje: str) -> IntentDetectionResult:
    """Example intent detection function."""
    mensaje_lower = mensaje.lower()
    
    intent_patterns = {
        IntencionType.SALUDO: ["hola", "buenas", "qué hubo", "saludos"],
        IntencionType.SALSA: ["salsa", "bailar", "baile", "topa tolondra"],
        IntencionType.GASTRONOMIA: ["comida", "restaurante", "comer", "gastronomía"],
        IntencionType.NATURALEZA: ["naturaleza", "río", "pance", "parque", "montaña"],
        IntencionType.CULTURA: ["cultura", "museo", "iglesia", "cristo rey", "historia"],
        IntencionType.EVENTOS: ["feria", "festival", "evento", "concierto"],
        IntencionType.RUTAS: ["ruta", "plan", "itinerario", "recorrido"],
        IntencionType.AYUDA: ["ayuda", "qué puedes hacer", "comandos"],
        IntencionType.AGRADECIMIENTO: ["gracias", "agradezco", "thanks"],
        IntencionType.DESPEDIDA: ["adiós", "chao", "hasta luego", "nos vemos"]
    }
    
    matches = {}
    for intent, keywords in intent_patterns.items():
        count = sum(1 for kw in keywords if kw in mensaje_lower)
        if count > 0:
            matches[intent] = count
    
    if not matches:
        return IntentDetectionResult(
            intencion=IntencionType.GENERAL,
            confianza=0.5,
            palabras_clave=[],
            entidades={}
        )
    
    best_intent = max(matches, key=matches.get)
    confidence = min(0.95, 0.3 + (matches[best_intent] / 20))
    
    return IntentDetectionResult(
        intencion=best_intent,
        confianza=confidence,
        palabras_clave=[kw for kw in intent_patterns[best_intent] if kw in mensaje_lower],
        entidades={}
    )


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("Chat schemas loaded successfully")
    print(f"Message roles: {RolMensaje.list_values()}")
    print(f"Intent types: {IntencionType.list_values()}")
    
    # Test intent display
    print("\nAvailable intents:")
    for intent in get_intenciones_disponibles():
        print(f"  {intent['label']} ({intent['value']})")
    
    # Test message request
    test_request = MensajeRequest(
        mensaje="¿Dónde puedo bailar salsa?",
        user_lat=3.4516,
        user_lng=-76.5320
    )
    print(f"\nTest request: {test_request.mensaje}")
    print(f"Has location: {test_request.tiene_ubicacion}")
    
    # Test intent detection
    test_messages = [
        "¿Dónde puedo bailar salsa?",
        "Recomiéndame un restaurante",
        "Quiero visitar el río Pance",
        "¿Cuándo es la Feria de Cali?"
    ]
    
    print("\nIntent detection test:")
    for msg in test_messages:
        result = detectar_intencion_ejemplo(msg)
        print(f"  '{msg}' -> {result.intencion.value} ({result.confianza_porcentaje}%)")
    
    # Test templates
    print("\nMessage templates:")
    for template in MESSAGE_TEMPLATES[:5]:
        print(f"  {template.intencion.value}: {template.template[:50]}...")
    
    print("\n✅ Chat schemas ready")