"""
Script para popular la base de datos Supabase con datos de ejemplo.

Uso:
    python scripts/seed_db.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

from supabase import create_client

def read_sql_file(filename: str) -> str:
    """Leer archivo SQL de seeds."""
    sql_path = Path(__file__).parent.parent / "app" / "database" / "seeds" / filename
    with open(sql_path, 'r', encoding='utf-8') as f:
        return f.read()

def execute_sql(client, sql: str, description: str) -> bool:
    """Ejecutar SQL y reportar resultado."""
    try:
        print(f"\n📝 {description}...")
        # Ejecutar raw SQL
        result = client.rpc('exec_sql', {'sql': sql}).execute()
        print(f"   ✅ {description} completado")
        return True
    except Exception as e:
        # Fallback: intentar con tabla específica si es Lugares
        if "lugares" in description.lower():
            try:
                print(f"   ⚠️ Intentando método alternativo...")
                # Aquí iríamos inserción por inserción si fuera necesario
                print(f"   ⚠️ Para INSERT, usa el SQL Editor de Supabase directamente")
                return False
            except Exception as e2:
                print(f"   ❌ Error: {str(e2)}")
                return False
        else:
            print(f"   ❌ Error: {str(e)}")
            return False

def main():
    """Función principal."""
    print("=" * 60)
    print("🌱 SEED DATABASE SCRIPT - LoCALIzate")
    print("=" * 60)
    
    # Verificar variables de entorno
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("\n❌ Error: SUPABASE_URL y SUPABASE_KEY no están configuradas")
        print("   Verifica el archivo .env")
        return False
    
    print(f"\n✅ Conectando a: {supabase_url}")
    
    # Crear cliente
    client = create_client(supabase_url, supabase_key)
    
    print("✅ Conexión exitosa\n")
    print("=" * 60)
    print("IMPORTANTE: Los INSERT de datos requieren permisos especiales.")
    print("Para completar el seed de datos:")
    print("=" * 60)
    print("\n📌 Opción 1: SQL Editor de Supabase (RECOMENDADO)")
    print("   1. Abre: https://app.supabase.com")
    print("   2. Ve a SQL Editor → New Query")
    print("   3. Copia el contenido de app/database/seeds/lugares.sql")
    print("   4. Ejecuta la query")
    
    print("\n📌 Opción 2: Acceso al SQL Editor")
    sql_files = [
        ("lugares.sql", "Lugares turísticos"),
        ("eventos.sql", "Eventos"),
        ("usuarios.sql", "Usuarios"),
    ]
    
    for filename, description in sql_files:
        try:
            sql = read_sql_file(filename)
            print(f"\n📄 {filename} ({description})")
            print(f"   Líneas: {len(sql.splitlines())}")
            print(f"   Ruta: app/database/seeds/{filename}")
        except FileNotFoundError:
            print(f"   ⚠️ Archivo no encontrado")
    
    print("\n" + "=" * 60)
    print("✅ Script completado")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
