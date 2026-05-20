"""
Configuration module for LoCALIzate Backend
==========================================

Centralized configuration management using Pydantic Settings.
Loads environment variables from .env file with validation.

Usage:
    from core.config import settings
    
    # Access settings
    print(settings.SUPABASE_URL)
    print(settings.APP_NAME)
"""

import os
from typing import List, Optional
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # =====================================================
    # APP CONFIGURATION
    # =====================================================
    APP_NAME: str = Field(default="LoCALIzate API", description="Nombre de la aplicación")
    APP_VERSION: str = Field(default="1.0.0", description="Versión de la API")
    APP_ENV: str = Field(default="development", description="Entorno: development, staging, production")
    DEBUG: bool = Field(default=True, description="Modo debug")
    API_PREFIX: str = Field(default="/api/v1", description="Prefijo para todas las rutas de API")
    
    # =====================================================
    # SERVER CONFIGURATION
    # =====================================================
    HOST: str = Field(default="0.0.0.0", description="Host del servidor")
    PORT: int = Field(default=5000, description="Puerto del servidor")
    RELOAD: bool = Field(default=True, description="Recarga automática en desarrollo")
    WORKERS: int = Field(default=1, description="Número de workers para producción")
    
    # =====================================================
    # CORS CONFIGURATION
    # =====================================================
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5000", "http://localhost:8000", "http://127.0.0.1:5000", "http://127.0.0.1:8000"],
        description="Orígenes permitidos para CORS"
    )
    CORS_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        description="Métodos HTTP permitidos"
    )
    CORS_HEADERS: List[str] = Field(
        default=["*"],
        description="Headers permitidos"
    )
    CORS_CREDENTIALS: bool = Field(default=True, description="Permitir credenciales")
    
    # =====================================================
    # SUPABASE CONFIGURATION
    # =====================================================
    SUPABASE_URL: str = Field(..., description="URL del proyecto Supabase")
    SUPABASE_KEY: str = Field(..., description="Clave anónima de Supabase")
    SUPABASE_SERVICE_KEY: Optional[str] = Field(None, description="Clave service_role de Supabase")
    SUPABASE_JWT_SECRET: Optional[str] = Field(default=None, description="JWT secret para verificar tokens")
    
    # =====================================================
    # DATABASE CONFIGURATION (PostgreSQL directo - opcional)
    # =====================================================
    DATABASE_URL: Optional[str] = Field(default=None, description="URL directa de PostgreSQL")
    DATABASE_POOL_SIZE: int = Field(default=10, description="Tamaño del pool de conexiones")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Máximo desbordamiento del pool")
    
    # =====================================================
    # REDIS CONFIGURATION (para caché y rate limiting)
    # =====================================================
    REDIS_URL: Optional[str] = Field(default=None, description="URL de Redis")
    REDIS_TTL: int = Field(default=3600, description="Tiempo de vida de caché en segundos")
    
    # =====================================================
    # RATE LIMITING
    # =====================================================
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Habilitar rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Número de requests permitidos")
    RATE_LIMIT_PERIOD: int = Field(default=60, description="Período en segundos")
    
    # =====================================================
    # JWT / AUTH CONFIGURATION
    # =====================================================
    JWT_ALGORITHM: str = Field(default="HS256", description="Algoritmo JWT")
    JWT_EXPIRATION_MINUTES: int = Field(default=1440, description="Expiración del token en minutos (24h)")
    
    # =====================================================
    # SERVICES CONFIGURATION
    # =====================================================
    # OSM (OpenStreetMap) Routing
    OSRM_URL: str = Field(default="https://router.project-osrm.org", description="URL del servicio OSRM")
    
    # Geocoding
    GEOCODING_PROVIDER: str = Field(default="osm", description="Proveedor de geocodificación: osm, google, here")
    GOOGLE_MAPS_API_KEY: Optional[str] = Field(default=None, description="API Key de Google Maps")
    HERE_API_KEY: Optional[str] = Field(default=None, description="API Key de HERE Maps")
    
    # Realidad Aumentada (AR)
    AR_ENABLED: bool = Field(default=True, description="Habilitar funcionalidades de AR")
    AR_API_URL: Optional[str] = Field(default=None, description="URL del servicio AR externo")
    
    # IA / Chat
    IA_ENABLED: bool = Field(default=True, description="Habilitar asistente IA")
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="API Key de OpenAI")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", description="Modelo de OpenAI a usar")
    IA_MAX_TOKENS: int = Field(default=500, description="Máximo de tokens por respuesta")
    IA_TEMPERATURE: float = Field(default=0.7, description="Temperatura para respuestas creativas")
    
    # =====================================================
    # FILE UPLOADS / STORAGE
    # =====================================================
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, description="Tamaño máximo de upload en MB")
    ALLOWED_IMAGE_TYPES: List[str] = Field(
        default=["image/jpeg", "image/png", "image/webp", "image/gif"],
        description="Tipos de imagen permitidos"
    )
    STORAGE_BUCKET: str = Field(default="LoCALIzate-assets", description="Bucket por defecto en Supabase Storage")
    
    # =====================================================
    # LOGGING
    # =====================================================
    LOG_LEVEL: str = Field(default="INFO", description="Nivel de logging: DEBUG, INFO, WARNING, ERROR")
    LOG_FORMAT: str = Field(default="json", description="Formato de logs: json o text")
    LOG_FILE: Optional[str] = Field(default="logs/app.log", description="Archivo de logs")
    
    # =====================================================
    # VALIDATORS
    # =====================================================
    @field_validator("APP_ENV")
    @classmethod
    def validate_env(cls, v: str) -> str:
        """Validar que el entorno sea válido."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"APP_ENV debe ser uno de: {allowed}")
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validar nivel de logging."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL debe ser uno de: {allowed}")
        return v.upper()
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parsear CORS origins desde string o lista."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # =====================================================
    # PROPERTIES
    # =====================================================
    @property
    def is_development(self) -> bool:
        """Retorna True si el entorno es development."""
        return self.APP_ENV == "development"
    
    @property
    def is_production(self) -> bool:
        """Retorna True si el entorno es production."""
        return self.APP_ENV == "production"
    
    @property
    def is_staging(self) -> bool:
        """Retorna True si el entorno es staging."""
        return self.APP_ENV == "staging"
    
    @property
    def supabase_client_config(self) -> dict:
        """Configuración para el cliente de Supabase."""
        return {
            "url": self.SUPABASE_URL,
            "key": self.SUPABASE_KEY,
            "service_key": self.SUPABASE_SERVICE_KEY,
        }
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignorar variables extras en .env


# =====================================================
# SINGLETON INSTANCE
# =====================================================

@lru_cache()
def get_settings() -> Settings:
    """
    Retorna una instancia cacheada de la configuración.
    Usar lru_cache para evitar recargar el .env en cada request.
    """
    return Settings()


# Instancia global para importar directamente
settings = get_settings()


# =====================================================
# VALIDACIÓN RÁPIDA (opcional, para debug)
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("LoCALIzate Backend - Configuration Check")
    print("=" * 50)
    print(f"APP_NAME: {settings.APP_NAME}")
    print(f"APP_ENV: {settings.APP_ENV}")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"SUPABASE_URL: {settings.SUPABASE_URL[:30]}..." if settings.SUPABASE_URL else "SUPABASE_URL: NOT SET")
    print(f"CORS_ORIGINS: {settings.CORS_ORIGINS}")
    print(f"RATE_LIMIT_ENABLED: {settings.RATE_LIMIT_ENABLED}")
    print(f"IA_ENABLED: {settings.IA_ENABLED}")
    print(f"LOG_LEVEL: {settings.LOG_LEVEL}")
    print("=" * 50)
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("⚠️  WARNING: SUPABASE_URL o SUPABASE_KEY no están configurados en .env")
    else:
        print("✅ Configuración válida")