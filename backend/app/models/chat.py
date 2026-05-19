"""
Chat Model for LoCALIzate Backend
================================

Models for the AI assistant chat functionality.
Handles conversations between users and the virtual tourist assistant.

Features:
    - Conversation history tracking
    - Message storage with role (user/assistant/system)
    - Intent detection for better responses
    - Place references in messages
    - Conversation metadata and analytics

Fields:
    - Conversacion: id, usuario_id, titulo, created_at, updated_at
    - Mensaje: id, conversacion_id, rol, contenido, intencion, lugares_referenciados
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
        """Get display name in Spanish."""
        names = {
            "user": "Usuario",
            "assistant": "Asistente",
            "system": "Sistema"
        }
        return names.get(value, value)
    
    @classmethod
    def get_icon(cls, value: str) -> str:
        """Get icon for message role."""
        icons = {
            "user": "👤",
            "assistant": "🤖",
            "system": "⚙️"
        }
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
        """Get display name in Spanish."""
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
# CONVERSACION MODELS
# =====================================================

class ConversacionBase(BaseModel):
    """Base model for Conversacion."""
    
    titulo: Optional[str] = Field(None, max_length=200, description="Título de la conversación")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "titulo": "Consulta sobre lugares turísticos en Cali"
            }
        }
    )


class ConversacionCreate(ConversacionBase):
    """Model for creating a new conversation."""
    
    usuario_id: Optional[str] = Field(None, description="ID del usuario (opcional, se asigna automáticamente)")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    
    @field_validator("titulo", mode="before")
    @classmethod
    def validate_titulo(cls, v: Optional[str]) -> str:
        """Generate default title if not provided."""
        if v:
            return v
        return f"Conversación {datetime.now().strftime('%Y-%m-%d %H:%M')}"


class ConversacionUpdate(BaseModel):
    """Model for updating a conversation."""
    
    titulo: Optional[str] = Field(None, max_length=200)


class ConversacionInDB(ConversacionBase):
    """Model representing a conversation as stored in database."""
    
    id: int = Field(..., description="ID único de la conversación")
    usuario_id: str = Field(..., description="ID del usuario")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    
    # Computed fields (from messages)
    mensaje_count: Optional[int] = Field(None, description="Número de mensajes en la conversación")
    ultimo_mensaje: Optional[str] = Field(None, description="Último mensaje enviado")
    ultimo_mensaje_fecha: Optional[datetime] = Field(None, description="Fecha del último mensaje")
    
    model_config = ConfigDict(from_attributes=True)
    
    @property
    def tiempo_desde_ultimo_mensaje(self) -> Optional[str]:
        """Get time since last message as human-readable string."""
        if not self.ultimo_mensaje_fecha:
            return None
        
        delta = datetime.now() - self.ultimo_mensaje_fecha
        if delta.days > 0:
            return f"hace {delta.days} día(s)"
        elif delta.seconds > 3600:
            return f"hace {delta.seconds // 3600} hora(s)"
        elif delta.seconds > 60:
            return f"hace {delta.seconds // 60} minuto(s)"
        return "hace unos segundos"


class ConversacionWithMessages(ConversacionInDB):
    """Conversation with all messages included."""
    
    messages: List["MensajeInDB"] = Field(default_factory=list, description="Mensajes de la conversación")


# =====================================================
# MENSAJE MODELS
# =====================================================

class MensajeBase(BaseModel):
    """Base model for Mensaje."""
    
    rol: RolMensaje = Field(..., description="Rol del emisor del mensaje")
    contenido: str = Field(..., min_length=1, max_length=2000, description="Contenido del mensaje")
    
    # Metadata
    intencion: Optional[IntencionType] = Field(None, description="Intención detectada del mensaje")
    lugares_referenciados: Optional[List[int]] = Field(None, description="IDs de lugares mencionados")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rol": "user",
                "contenido": "¿Cuáles son los mejores lugares para bailar salsa en Cali?",
                "intencion": "salsa"
            }
        }
    )
    
    @field_validator("contenido")
    @classmethod
    def validate_contenido(cls, v: str) -> str:
        """Validate and clean message content."""
        v = v.strip()
        if not v:
            raise ValueError("El mensaje no puede estar vacío")
        return v


class MensajeCreate(MensajeBase):
    """Model for creating a new message."""
    
    conversacion_id: Optional[int] = Field(None, description="ID de la conversación (opcional, se crea nueva si no existe)")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    
    @field_validator("lugares_referenciados", mode="before")
    @classmethod
    def validate_lugares_referenciados(cls, v: Optional[List]) -> Optional[List]:
        """Validate and clean referenced places list."""
        if v is None:
            return []
        
        # Remove duplicates and None values
        return list(set([int(x) for x in v if x is not None]))


class MensajeInDB(MensajeBase):
    """Model representing a message as stored in database."""
    
    id: int = Field(..., description="ID único del mensaje")
    conversacion_id: int = Field(..., description="ID de la conversación")
    created_at: datetime = Field(..., description="Fecha de creación")
    
    model_config = ConfigDict(from_attributes=True)
    
    @property
    def es_usuario(self) -> bool:
        """Check if message is from user."""
        return self.rol == RolMensaje.USER
    
    @property
    def es_asistente(self) -> bool:
        """Check if message is from assistant."""
        return self.rol == RolMensaje.ASSISTANT
    
    @property
    def es_sistema(self) -> bool:
        """Check if message is from system."""
        return self.rol == RolMensaje.SYSTEM
    
    @property
    def preview(self) -> str:
        """Get message preview (first 100 chars)."""
        if len(self.contenido) <= 100:
            return self.contenido
        return self.contenido[:97] + "..."


# =====================================================
# CHAT REQUEST/RESPONSE MODELS
# =====================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    
    mensaje: str = Field(..., min_length=1, max_length=2000, description="Mensaje del usuario")
    conversacion_id: Optional[int] = Field(None, description="ID de conversación existente (opcional)")
    
    # Context information
    user_lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitud actual del usuario")
    user_lng: Optional[float] = Field(None, ge=-180, le=180, description="Longitud actual del usuario")
    
    @field_validator("mensaje")
    @classmethod
    def validate_mensaje(cls, v: str) -> str:
        """Validate and clean message."""
        v = v.strip()
        if not v:
            raise ValueError("El mensaje no puede estar vacío")
        return v
    
    @property
    def tiene_ubicacion(self) -> bool:
        """Check if user location is provided."""
        return self.user_lat is not None and self.user_lng is not None


class LugarSugerido(BaseModel):
    """Suggested place from chat response."""
    
    id: int
    nombre: str
    descripcion_corta: Optional[str] = None
    latitud: float
    longitud: float
    icono: str = "📍"
    rating: float = 0.0
    distancia_km: Optional[float] = None
    direccion: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    
    respuesta: str = Field(..., description="Respuesta del asistente")
    conversacion_id: int = Field(..., description="ID de la conversación")
    mensaje_id: int = Field(..., description="ID del mensaje del asistente")
    intencion: IntencionType = Field(..., description="Intención detectada")
    
    # Additional data
    lugares_sugeridos: List[LugarSugerido] = Field(default_factory=list, description="Lugares sugeridos")
    sugerencias: List[str] = Field(default_factory=list, description="Sugerencias de preguntas relacionadas")
    
    # Context for follow-up
    contexto: Optional[Dict[str, Any]] = Field(None, description="Contexto para seguimiento")


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    
    conversaciones: List[ConversacionInDB] = Field(default_factory=list)
    total: int = 0


class ChatConversationDetailResponse(BaseModel):
    """Response model for conversation details."""
    
    conversacion: ConversacionInDB
    mensajes: List[MensajeInDB]


# =====================================================
# INTENT DETECTION MODELS
# =====================================================

class IntentDetectionResult(BaseModel):
    """Result of intent detection."""
    
    intencion: IntencionType
    confianza: float = Field(..., ge=0, le=1, description="Confianza de la detección (0-1)")
    palabras_clave: List[str] = Field(default_factory=list, description="Palabras clave que activaron la intención")
    entidades: Dict[str, Any] = Field(default_factory=dict, description="Entidades extraídas")
    
    @property
    def es_alta_confianza(self) -> bool:
        """Check if confidence is high (>0.7)."""
        return self.confianza > 0.7
    
    @property
    def confianza_porcentaje(self) -> int:
        """Get confidence as percentage."""
        return int(self.confianza * 100)


# =====================================================
# MESSAGE TEMPLATES
# =====================================================

class MessageTemplate(BaseModel):
    """Template for assistant responses."""
    
    intencion: IntencionType
    template: str
    requires_context: bool = False
    examples: List[str] = Field(default_factory=list)


# Predefined message templates for different intents
MESSAGE_TEMPLATES: List[MessageTemplate] = [
    MessageTemplate(
        intencion=IntencionType.SALUDO,
        template="¡Qué hubo, parcero! 🎭 Soy tu asistente turístico de Cali. ¿En qué puedo ayudarte hoy?",
        examples=["Hola", "Buenos días", "Qué hubo"]
    ),
    MessageTemplate(
        intencion=IntencionType.SALSA,
        template="¡La salsa es el alma de Cali! 🎺 Te recomiendo visitar La Topa Tolondra, Tin Tin Deo o la Plazoleta Jairo Varela. El Festival Mundial de Salsa es del 24-28 de Septiembre 2026.",
        examples=["dónde bailar salsa", "mejores bares de salsa", "clases de baile"]
    ),
    MessageTemplate(
        intencion=IntencionType.GASTRONOMIA,
        template="Cali es un paraíso gastronómico 🍽️. Prueba Morada Ancestral (cocina del Pacífico), Palomulata Parrilla o el Tour Gastronómico del Pacífico los sábados.",
        examples=["restaurantes", "comida típica", "dónde comer"]
    ),
    MessageTemplate(
        intencion=IntencionType.NATURALEZA,
        template="Para conectar con la naturaleza 🌳 te recomiendo el Río Pance, los Farallones de Cali (trekking), el Zoológico de Cali o la Chorrera del Indio.",
        examples=["parques", "ríos", "montañas", "senderismo"]
    ),
    MessageTemplate(
        intencion=IntencionType.CULTURA,
        template="Descubre la cultura caleña 🎭 visitando el Cristo Rey, la Iglesia La Ermita, el Museo del Oro Calima y el Barrio San Antonio.",
        examples=["museos", "historia", "iglesias", "arte"]
    ),
    MessageTemplate(
        intencion=IntencionType.EVENTOS,
        template="Los eventos más importantes de Cali 2026 📅: Feria de Cali (25-30 Dic), Festival Mundial de Salsa (24-28 Sep), Petronio Álvarez (14-19 Ago).",
        examples=["feria", "festivales", "conciertos", "qué hacer"]
    ),
    MessageTemplate(
        intencion=IntencionType.RUTAS,
        template="¡Perfecto! 🗺️ Usa el Planificador Inteligente en la pestaña 'Plan Ruta'. Selecciona hasta 5 lugares y te optimizo la ruta más corta desde tu ubicación.",
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
        examples=["adiós", "chao", "hasta luego", "nos vemos"]
    ),
    MessageTemplate(
        intencion=IntencionType.AYUDA,
        template="Puedo ayudarte con información sobre 🎺 salsa, 🍽️ restaurantes, 🌳 naturaleza, 🎭 cultura, 📅 eventos y 🗺️ planificación de rutas en Cali. ¿Qué te gustaría saber?",
        examples=["ayuda", "qué puedes hacer", "comandos"]
    )
]


def get_template_by_intent(intencion: IntencionType) -> Optional[MessageTemplate]:
    """Get message template by intent."""
    for template in MESSAGE_TEMPLATES:
        if template.intencion == intencion:
            return template
    return None


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def detectar_intencion(texto: str) -> IntentDetectionResult:
    """
    Detect user intent from message text.
    
    Args:
        texto: User message text
    
    Returns:
        IntentDetectionResult with intent and confidence
    """
    texto_lower = texto.lower()
    
    # Intent patterns
    intent_patterns = {
        IntencionType.SALUDO: ["hola", "buenas", "quihubo", "qué hubo", "saludos", "buenos días", "buenas tardes"],
        IntencionType.SALSA: ["salsa", "bailar", "baile", "topa tolondra", "tin tin", "salsero", "rumba"],
        IntencionType.GASTRONOMIA: ["comida", "restaurante", "gastro", "comer", "parrilla", "morada ancestral", "bulevar", "lulada", "cholado"],
        IntencionType.NATURALEZA: ["naturaleza", "montaña", "río", "pance", "farallones", "cascada", "senderismo", "zoológico"],
        IntencionType.CULTURA: ["cultura", "museo", "iglesia", "teatro", "ermita", "cristo rey", "gato del río", "historia"],
        IntencionType.EVENTOS: ["feria", "festival", "evento", "concierto", "petronio", "salsódromo", "cabalgata"],
        IntencionType.RUTAS: ["ruta", "plan", "viaje", "recorrido", "itinerario", "optimizar", "visitar"],
        IntencionType.HORARIOS: ["horario", "abre", "cierra", "cuándo", "hora"],
        IntencionType.PRECIOS: ["precio", "cuesta", "valor", "entrada", "boleta", "gratis"],
        IntencionType.UBICACION: ["ubicación", "dirección", "donde queda", "cómo llegar", "mapa"],
        IntencionType.AGRADECIMIENTO: ["gracias", "agradezco", "thanks", "muchas gracias"],
        IntencionType.DESPEDIDA: ["adiós", "chao", "hasta luego", "nos vemos", "bye"],
        IntencionType.AYUDA: ["ayuda", "qué puedes hacer", "cómo funciona", "comandos"]
    }
    
    # Count matches
    matches = {}
    for intent, keywords in intent_patterns.items():
        count = sum(1 for keyword in keywords if keyword in texto_lower)
        if count > 0:
            matches[intent] = count
    
    if not matches:
        return IntentDetectionResult(
            intencion=IntencionType.GENERAL,
            confianza=0.5,
            palabras_clave=[],
            entidades={}
        )
    
    # Get intent with highest match count
    best_intent = max(matches, key=matches.get)
    max_matches = matches[best_intent]
    
    # Calculate confidence (simple heuristic)
    total_keywords = sum(len(keywords) for keywords in intent_patterns.values())
    confidence = min(0.95, 0.3 + (max_matches / total_keywords) * 0.5)
    
    return IntentDetectionResult(
        intencion=best_intent,
        confianza=confidence,
        palabras_clave=[kw for kw in intent_patterns[best_intent] if kw in texto_lower],
        entidades={}
    )


def generar_respuesta_basica(intencion: IntencionType, contexto: Optional[Dict] = None) -> str:
    """Generate basic response based on intent."""
    template = get_template_by_intent(intencion)
    if template:
        return template.template
    
    # Default responses
    default_responses = {
        IntencionType.GENERAL: "¡Con gusto te ayudo! Puedo responderte sobre salsa, gastronomía, naturaleza, cultura, eventos y rutas en Cali. ¿Qué te gustaría saber?",
        IntencionType.HORARIOS: "Los horarios varían según el lugar. Te recomiendo usar el planificador de rutas para ver los horarios específicos de cada atracción.",
        IntencionType.PRECIOS: "Los precios pueden variar. Muchos lugares son gratuitos o tienen precios accesibles. Usa el filtro de precio en la sección de lugares para más detalles.",
        IntencionType.UBICACION: "Para ver la ubicación exacta, haz clic en cualquier lugar del mapa o usa la función '¿Dónde estoy?' para encontrar sitios cercanos."
    }
    
    return default_responses.get(intencion, default_responses[IntencionType.GENERAL])


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("Chat model loaded successfully")
    print(f"Message roles: {RolMensaje.list_values()}")
    print(f"Intent types: {IntencionType.list_values()}")
    
    # Test intent detection
    test_messages = [
        "¿Dónde puedo bailar salsa en Cali?",
        "Recomiéndame un buen restaurante",
        "Quiero visitar el río Pance",
        "¿Cuándo es la Feria de Cali?",
        "Hola, ¿qué tal?",
        "Gracias por la información"
    ]
    
    print("\nIntent detection test:")
    for msg in test_messages:
        result = detectar_intencion(msg)
        print(f"  '{msg}' -> {result.intencion.value} (confianza: {result.confianza_porcentaje}%)")
    
    # Test message creation
    test_mensaje = MensajeCreate(
        rol=RolMensaje.USER,
        contenido="¿Cuáles son los mejores lugares turísticos?",
        intencion=IntencionType.LUGARES
    )
    print(f"\nTest message created: {test_mensaje.contenido[:50]}...")
    
    # Test conversation
    test_conversacion = ConversacionCreate(
        titulo="Consulta sobre Cali"
    )
    print(f"Test conversation: {test_conversacion.titulo}")
    
    print("\n✅ Chat model ready")