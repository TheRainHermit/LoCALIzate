from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import (
    lugares, eventos, gastronomia, usuarios,
    rutas, recomendaciones, auth, vision
)
from app.config import settings

# Lifespan: ejecuta código al iniciar y cerrar la app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 CaliGuía Backend iniciando...")
    await init_ml_models()  # Cargar modelos de ML
    yield
    # Shutdown
    print("🛑 CaliGuía Backend cerrando...")

app = FastAPI(
    title="CaliGuía - Asistente Turístico Inteligente",
    version="1.0.0",
    lifespan=lifespan
)

# CORS para permitir requests desde web y mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "exp://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["usuarios"])
app.include_router(lugares.router, prefix="/api/lugares", tags=["lugares"])
app.include_router(eventos.router, prefix="/api/eventos", tags=["eventos"])
app.include_router(gastronomia.router, prefix="/api/gastronomia", tags=["gastronomia"])
app.include_router(rutas.router, prefix="/api/rutas", tags=["rutas"])
app.include_router(recomendaciones.router, prefix="/api/recomendaciones", tags=["recomendaciones"])
app.include_router(vision.router, prefix="/api/vision", tags=["vision"])

@app.get("/health")
async def health():
    return { "status": "ok", "timestamp": datetime.now() }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)