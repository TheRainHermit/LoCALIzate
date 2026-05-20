"""
Script de verificación para LoCALIzate / CaliGuia Backend
Ejecuta este script para comprobar que todas las conexiones funcionan

Uso:
    python test_connection.py
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def test_environment_variables():
    """Verificar que las variables de entorno están configuradas"""
    print("\n" + "=" * 60)
    print("📋 VERIFICANDO VARIABAS DE ENTORNO")
    print("=" * 60)

    required_vars = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
        "SUPABASE_SERVICE_KEY": os.getenv("SUPABASE_SERVICE_KEY"),
    }

    optional_vars = {
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "APP_ENV": os.getenv("APP_ENV", "development"),
        "DEBUG": os.getenv("DEBUG", "true"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    }

    all_ok = True
    print("\n📌 Variables requeridas:")
    for var_name, var_value in required_vars.items():
        if var_value:
            # Mostrar solo primeros caracteres por seguridad
            display_value = var_value[:20] + "..." if len(var_value) > 20 else var_value
            print(f"   ✅ {var_name}: {display_value}")
        else:
            print(f"   ❌ {var_name}: NO CONFIGURADA")
            all_ok = False

    print("\n📌 Variables opcionales:")
    for var_name, var_value in optional_vars.items():
        if var_value:
            print(f"   ✅ {var_name}: {var_value}")
        else:
            print(f"   ⚠️ {var_name}: no configurada (usando valor por defecto)")

    return all_ok


def test_dependencies():
    """Verificar que todas las dependencias están instaladas"""
    print("\n" + "=" * 60)
    print("📦 VERIFICANDO DEPENDENCIAS")
    print("=" * 60)

    dependencies = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "supabase": "Supabase",
        "pydantic": "Pydantic",
        "pydantic_settings": "Pydantic Settings",
        "python_dotenv": "python-dotenv",
        "httpx": "HTTPX",
        "jose": "python-jose",
    }

    all_ok = True
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {name}: instalado")
        except ImportError:
            print(f"   ❌ {name}: NO INSTALADO")
            all_ok = False

    if not all_ok:
        print("\n📌 Instala las dependencias faltantes con:")
        print("   pip install -r requirements.txt")

    return all_ok


def test_supabase_connection():
    """Verificar conexión con Supabase"""
    print("\n" + "=" * 60)
    print("🗄️ VERIFICANDO CONEXIÓN CON SUPABASE")
    print("=" * 60)

    try:
        from supabase import create_client

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            print("   ❌ Supabase no configurado - faltan URL o KEY")
            return False

        print("   🔌 Conectando a Supabase...")
        client = create_client(supabase_url, supabase_key)

        # Probar consulta simple
        print("   📡 Probando consulta a tabla 'categorias'...")
        response = client.table("categorias").select("*").limit(1).execute()

        print(f"   ✅ Conexión exitosa! Datos recibidos: {len(response.data)} registros")

        # Verificar tablas necesarias
        print("\n   📊 Verificando tablas...")
        tables = ["categorias", "lugares", "eventos", "usuarios", "rutas_usuario", "favoritos", "resenas"]

        for table in tables:
            try:
                result = client.table(table).select("*", count="exact").limit(0).execute()
                count = result.count if hasattr(result, 'count') else "desconocido"
                print(f"      ✅ Tabla '{table}': {count} registros")
            except Exception as e:
                print(f"      ⚠️ Tabla '{table}': {str(e)[:50]}...")

        return True

    except ImportError:
        print("   ❌ Supabase library no instalada. Ejecuta: pip install supabase")
        return False
    except Exception as e:
        print(f"   ❌ Error conectando a Supabase: {e}")
        return False


def test_fastapi_app():
    """Verificar que FastAPI se puede inicializar correctamente"""
    print("\n" + "=" * 60)
    print("🚀 VERIFICANDO FASTAPI")
    print("=" * 60)

    try:
        from fastapi import FastAPI
        print("   ✅ FastAPI instalado correctamente")
        return True
    except ImportError:
        print("   ❌ FastAPI no instalado. Ejecuta: pip install fastapi uvicorn")
        return False


def test_api_endpoints():
    """Probar los endpoints de la API localmente"""
    print("\n" + "=" * 60)
    print("🌐 PROBANDO ENDPOINTS DE LA API")
    print("=" * 60)

    try:
        import httpx

        base_url = "http://localhost:5000"

        print(f"   🔌 Probando conexión a {base_url}...")

        # Probar endpoint de salud
        try:
            response = httpx.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Servidor corriendo en {base_url}")
                print(f"      Health: {data.get('status', 'unknown')}")
            else:
                print(f"   ⚠️ Servidor respondiendo pero con status {response.status_code}")
                return None
        except httpx.ConnectError:
            print("   ⚠️ Servidor no está corriendo localmente")
            print("      Para probar endpoints, inicia el servidor con: python main.py")
            return None

        # Probar endpoint raíz
        response = httpx.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Endpoint raíz: {data.get('name', 'OK')} v{data.get('version', 'unknown')}")

        # Probar endpoint de lugares
        response = httpx.get(f"{base_url}/api/v1/lugares/?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            lugares = data.get('results', data.get('lugares', []))
            print(f"   ✅ Lugares endpoint: {len(lugares)} lugares obtenidos")

        # Probar endpoint de eventos
        response = httpx.get(f"{base_url}/api/v1/eventos/?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            eventos = data.get('results', data.get('eventos', []))
            print(f"   ✅ Eventos endpoint: {len(eventos)} eventos obtenidos")

        return True

    except ImportError:
        print("   ⚠️ httpx no instalado. Instala con: pip install httpx")
        return None
    except Exception as e:
        print(f"   ⚠️ Error probando endpoints: {e}")
        return None


def test_secret_key():
    """Verificar que la SECRET_KEY es segura"""
    print("\n" + "=" * 60)
    print("🔒 VERIFICANDO SECRET_KEY")
    print("=" * 60)

    secret_key = os.getenv("SECRET_KEY")

    if not secret_key:
        print("   ⚠️ SECRET_KEY no configurada (no es obligatoria para desarrollo)")
        return True

    # Verificar longitud mínima
    if len(secret_key) < 32:
        print(f"   ⚠️ SECRET_KEY corta: {len(secret_key)} caracteres (recomendado: 32+)")
    else:
        print(f"   ✅ SECRET_KEY longitud adecuada: {len(secret_key)} caracteres")

    # Verificar que no es la clave por defecto
    default_keys = ["tu_secret_key_para_jwt", "secret-key", "changeme", "password", "laquitoporseguridad"]
    if secret_key.lower() in default_keys:
        print("   ⚠️ SECRET_KEY es una clave por defecto - CAMBIALA en producción!")
    else:
        print("   ✅ SECRET_KEY no es una clave por defecto")

    return True


def test_database_data():
    """Verificar que hay datos en las tablas"""
    print("\n" + "=" * 60)
    print("📊 VERIFICANDO DATOS EN SUPABASE")
    print("=" * 60)

    try:
        from supabase import create_client

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            return False

        client = create_client(supabase_url, supabase_key)

        # Contar registros en cada tabla
        tables_to_check = {
            "categorias": "Categorías",
            "lugares": "Lugares",
            "eventos": "Eventos",
            "usuarios": "Usuarios",
            "favoritos": "Favoritos",
            "resenas": "Reseñas",
            "rutas_usuario": "Rutas",
        }

        for table, name in tables_to_check.items():
            try:
                result = client.table(table).select("*", count="exact").limit(0).execute()
                count = result.count if hasattr(result, 'count') else 0
                print(f"   📁 {name}: {count} registros")
            except Exception as e:
                print(f"   ⚠️ {name}: Error - {str(e)[:50]}")

        return True

    except Exception as e:
        print(f"   ❌ Error verificando datos: {e}")
        return False


def test_services_import():
    """Verificar que los servicios se pueden importar correctamente"""
    print("\n" + "=" * 60)
    print("🔧 VERIFICANDO SERVICIOS")
    print("=" * 60)

    services = [
        ("app.services.ar_service", "AR Service"),
        ("app.services.asistente_ia", "Asistente IA"),
        ("app.services.geocoding_osm", "Geocoding OSM"),
        ("app.services.optimizador_rutas", "Optimizador de Rutas"),
        ("app.services.recommendation", "Recomendaciones"),
    ]

    all_ok = True
    for module_path, name in services:
        try:
            __import__(module_path)
            print(f"   ✅ {name}: importado correctamente")
        except ImportError as e:
            print(f"   ❌ {name}: error - {str(e)[:50]}")
            all_ok = False

    return all_ok


def test_middleware_import():
    """Verificar que los middlewares se pueden importar correctamente"""
    print("\n" + "=" * 60)
    print("🛡️ VERIFICANDO MIDDLEWARES")
    print("=" * 60)

    middlewares = [
        ("app.middleware.auth", "Auth Middleware"),
        ("app.middleware.logging", "Logging Middleware"),
        ("app.middleware.rate_limit", "Rate Limit Middleware"),
    ]

    all_ok = True
    for module_path, name in middlewares:
        try:
            __import__(module_path)
            print(f"   ✅ {name}: importado correctamente")
        except ImportError as e:
            print(f"   ❌ {name}: error - {str(e)[:50]}")
            all_ok = False

    return all_ok


def main():
    """Función principal de verificación"""
    print("\n" + "🎭" * 30)
    print("   LoCALIzate / CaliGuia BACKEND - VERIFICACIÓN")
    print("🎭" * 30)

    results = {}

    # Ejecutar todas las pruebas
    results["variables"] = test_environment_variables()
    results["dependencies"] = test_dependencies()
    results["fastapi"] = test_fastapi_app()
    results["supabase"] = test_supabase_connection()
    results["database_data"] = test_database_data()
    results["services"] = test_services_import()
    results["middleware"] = test_middleware_import()
    results["secret_key"] = test_secret_key()
    results["api_endpoints"] = test_api_endpoints()

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)

    for test_name, passed in results.items():
        if passed is True:
            print(f"   ✅ {test_name.upper()}: OK")
        elif passed is False:
            print(f"   ❌ {test_name.upper()}: FALLÓ")
        else:
            print(f"   ⚠️ {test_name.upper()}: ADVERTENCIA")

    # Recomendaciones
    print("\n" + "=" * 60)
    print("💡 RECOMENDACIONES")
    print("=" * 60)

    if not results.get("dependencies"):
        print("   1. Instala las dependencias: pip install -r requirements.txt")

    if not results.get("supabase"):
        print("   2. Verifica que SUPABASE_URL y SUPABASE_KEY son correctos")
        print("      Puedes encontrar estas claves en Supabase Dashboard > Project Settings > API")

    if results.get("api_endpoints") is None:
        print("   3. Inicia el servidor local para probar endpoints:")
        print("      python main.py")
        print("   O con uvicorn: uvicorn main:app --reload")

    print("\n" + "🎭" * 30)
    print("   ¡VERIFICACIÓN COMPLETADA!")
    print("🎭" * 30 + "\n")


if __name__ == "__main__":
    main()