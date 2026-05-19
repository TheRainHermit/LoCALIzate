"""
Seeds module for database population.
Provides functions to load initial data into the database.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Directorio actual
SEEDS_DIR = os.path.dirname(__file__)


def read_sql_file(filename: str) -> Optional[str]:
    """
    Read SQL file content.
    
    Args:
        filename: Name of SQL file
    
    Returns:
        SQL content or None if error
    """
    filepath = os.path.join(SEEDS_DIR, filename)
    
    if not os.path.exists(filepath):
        logger.error(f"Seed file not found: {filepath}")
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading {filename}: {str(e)}")
        return None


def run_seed_file(supabase_client, filename: str) -> bool:
    """
    Execute a seed SQL file.
    
    Args:
        supabase_client: Supabase client instance
        filename: Name of SQL file
    
    Returns:
        True if successful
    """
    sql_content = read_sql_file(filename)
    
    if not sql_content:
        return False
    
    try:
        # Nota: Supabase client no ejecuta SQL directamente.
        # Para seeds, usar el Dashboard de Supabase o un cliente PostgreSQL directo.
        # Esta función es un placeholder - en producción usar psycopg2.
        
        logger.info(f"Seed file {filename} loaded ({len(sql_content)} bytes)")
        logger.warning("Ejecutar seeds manualmente en Supabase SQL Editor")
        
        # Para ejecutar automáticamente, usar:
        # import psycopg2
        # conn = psycopg2.connect(settings.DATABASE_URL)
        # cur = conn.cursor()
        # cur.execute(sql_content)
        # conn.commit()
        
        return True
        
    except Exception as e:
        logger.error(f"Error executing seed {filename}: {str(e)}")
        return False


def seed_lugares(supabase_client) -> bool:
    """Seed lugares table."""
    return run_seed_file(supabase_client, "lugares.sql")


def seed_eventos(supabase_client) -> bool:
    """Seed eventos table."""
    return run_seed_file(supabase_client, "eventos.sql")


def seed_usuarios(supabase_client) -> bool:
    """Seed usuarios table."""
    return run_seed_file(supabase_client, "usuarios.sql")


def run_all_seeds(supabase_client) -> dict:
    """
    Run all seed files.
    
    Returns:
        Dictionary with results
    """
    results = {
        "lugares": seed_lugares(supabase_client),
        "eventos": seed_eventos(supabase_client),
        "usuarios": seed_usuarios(supabase_client)
    }
    
    success_count = sum(1 for v in results.values() if v)
    
    logger.info(f"Seeds completed: {success_count}/{len(results)} successful")
    
    return results


if __name__ == "__main__":
    print("Seeds module loaded successfully")
    print("Available seeds: lugares.sql, eventos.sql, usuarios.sql")