from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Lugar(BaseModel):
    id: int
    nombre: str
    lat: float
    lng: float
    interes: str
    rating: float
    rating_count: str
    horario: str
    precio: str
    direccion: str
    descripcion: str
    tip_caleño: str
    historia: str
    datos_curiosos: List[str]
    imagen: str

class Evento(BaseModel):
    id: int
    nombre: str
    fecha_inicio: str
    fecha_fin: str
    descripcion: str
    ubicacion: str
    destacado: bool
    precio: str
    horario: str
    actividades: List[str]

class RutaRequest(BaseModel):
    lugares_ids: List[int]
    origen_lat: float
    origen_lng: float

class RutaResponse(BaseModel):
    lugares_ordenados: List[Lugar]
    distancia_total: float
    pasos: List[dict]

class MensajeChat(BaseModel):
    mensaje: str
    usuario_id: Optional[int] = None

class RespuestaChat(BaseModel):
    respuesta: str
    sugerencias: List[str]
    lugares_recomendados: Optional[List[dict]] = None

class PreferenciasUsuario(BaseModel):
    usuario_id: int
    intereses: List[str]