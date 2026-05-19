"""
Alembic environment configuration for database migrations.
Ejecuta migraciones en Supabase/PostgreSQL.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Agregar el directorio padre al path para importar modelos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Importar modelos para que Alembic los detecte
try:
    from database.models import (
        Lugar, Evento, Usuario, RutaUsuario, 
        RutaDetalle, Favorito, Resena, Categoria
    )
    from app.database.supabase_client import supabase_client
except ImportError:
    # Si no se pueden importar, continuar sin modelos
    pass

# Este es el objeto MetaData de SQLAlchemy que contiene todas las tablas
# Si tienes un Base declarativo, impórtalo aquí
# from app.models import Base
# target_metadata = Base.metadata

target_metadata = None

# Configuración de logging
config = context.config
fileConfig(config.config_file_name) if config.config_file_name else None


def get_db_url() -> str:
    """
    Obtener URL de la base de datos desde variables de entorno.
    """
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    
    # Para PostgreSQL directo (requiere conexión directa a la DB)
    # Formato: postgresql://postgres:password@db.supabase.co:5432/postgres
    direct_url = os.getenv("DATABASE_URL", "")
    
    if direct_url:
        return direct_url
    
    # Si no hay URL directa, usar la de Supabase con el pooler
    # Esto requiere configurar una conexión directa a PostgreSQL
    supabase_host = supabase_url.replace("https://", "").replace(".supabase.co", "")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    
    if supabase_host and db_password:
        return f"postgresql://{db_user}:{db_password}@db.{supabase_host}.supabase.co:5432/postgres"
    
    raise ValueError("No se encontró URL de base de datos. Configure DATABASE_URL en .env")


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = get_db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_db_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()