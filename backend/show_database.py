#!/usr/bin/env python
"""
Script para mostrar la información de la base de datos en Supabase.
Ejecutar: python show_database.py
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.supabase_client import supabase_client


def print_separator(char="=", length=60):
    """Imprimir línea separadora."""
    print(char * length)


def print_header(title):
    """Imprimir título formateado."""
    print_separator()
    print(f"📊 {title}")
    print_separator()


def print_table(title, data, headers=None):
    """Imprimir tabla formateada."""
    if not data:
        print(f"   ℹ️ No hay datos en {title}")
        return
    
    print(f"\n📁 {title}:")
    print_separator("-")
    
    for i, row in enumerate(data[:10], 1):  # Mostrar solo primeros 10
        print(f"   {i}. {row}")
    
    if len(data) > 10:
        print(f"   ... y {len(data) - 10} más")


def main():
    """Función principal."""
    print_separator("=", 60)
    print("   🗄️  LoCALIzate / CaliGuia - Database Viewer")
    print_separator("=", 60)
    
    # Verificar conexión
    print("\n🔌 Verificando conexión a Supabase...")
    
    try:
        client = supabase_client.get_client()
        # Probar conexión
        test = client.table("categorias").select("count", count="exact").limit(1).execute()
        print("   ✅ Conexión exitosa!")
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
        return
    
    print(f"\n📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # =====================================================
    # 1. TABLA CATEGORÍAS
    # =====================================================
    print_header("CATEGORÍAS")
    try:
        result = client.table("categorias").select("*").order("orden").execute()
        categorias = result.data if result.data else []
        
        print(f"\n   Total: {len(categorias)} categorías")
        
        for cat in categorias:
            print(f"   • {cat.get('icono', '📍')} {cat.get('nombre')} ({cat.get('slug')})")
            if cat.get('descripcion'):
                print(f"     📝 {cat.get('descripcion')[:80]}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # =====================================================
    # 2. TABLA LUGARES
    # =====================================================
    print_header("LUGARES TURÍSTICOS")
    try:
        result = client.table("lugares").select("*").eq("activo", True).order("rating", desc=True).execute()
        lugares = result.data if result.data else []
        
        print(f"\n   Total: {len(lugares)} lugares")
        
        # Estadísticas por interés
        intereses = {}
        for lugar in lugares:
            interes = lugar.get('interes', 'sin_interes')
            intereses[interes] = intereses.get(interes, 0) + 1
        
        print("\n   📈 Distribución por interés:")
        for interes, count in sorted(intereses.items()):
            iconos = {
                'cultura': '🎭', 'naturaleza': '🌳', 'gastronomia': '🍽️',
                'salsa': '💃', 'aventura': '🧗'
            }
            icono = iconos.get(interes, '📍')
            print(f"      {icono} {interes}: {count} lugares")
        
        # Top 5 lugares mejor calificados
        print("\n   ⭐ Top 5 lugares mejor calificados:")
        for i, lugar in enumerate(lugares[:5], 1):
            nombre = lugar.get('nombre', 'N/A')
            rating = lugar.get('rating', 0)
            interes = lugar.get('interes', 'N/A')
            print(f"      {i}. {nombre} - ⭐ {rating} ({interes})")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # =====================================================
    # 3. TABLA EVENTOS
    # =====================================================
    print_header("EVENTOS")
    try:
        result = client.table("eventos").select("*").eq("activo", True).order("fecha_inicio").execute()
        eventos = result.data if result.data else []
        
        print(f"\n   Total: {len(eventos)} eventos")
        
        # Eventos próximos
        from datetime import date
        today = date.today().isoformat()
        proximos = [e for e in eventos if e.get('fecha_inicio', '') >= today]
        
        print(f"\n   📅 Eventos próximos ({len(proximos)}):")
        for evento in proximos[:5]:
            nombre = evento.get('nombre', 'N/A')
            fecha = evento.get('fecha_inicio', 'N/A')
            ubicacion = evento.get('ubicacion', 'N/A')
            print(f"      • {nombre}")
            print(f"        📅 {fecha} | 📍 {ubicacion}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # =====================================================
    # 4. TABLA USUARIOS
    # =====================================================
    print_header("USUARIOS")
    try:
        result = client.table("usuarios").select("*").execute()
        usuarios = result.data if result.data else []
        
        print(f"\n   Total: {len(usuarios)} usuarios registrados")
        
        for usuario in usuarios[:5]:
            nombre = usuario.get('nombre', usuario.get('email', 'N/A'))
            email = usuario.get('email', 'N/A')
            ciudad = usuario.get('ciudad', 'N/A')
            print(f"      • {nombre}")
            print(f"        📧 {email} | 📍 {ciudad}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # =====================================================
    # 5. TABLA RUTAS
    # =====================================================
    print_header("RUTAS GUARDADAS")
    try:
        result = client.table("rutas_usuario").select("*").execute()
        rutas = result.data if result.data else []
        
        print(f"\n   Total: {len(rutas)} rutas guardadas")
        
        for ruta in rutas[:5]:
            nombre = ruta.get('nombre', 'N/A')
            usuario_id = ruta.get('usuario_id', 'N/A')
            created_at = ruta.get('created_at', 'N/A')
            print(f"      • {nombre} (usuario: {usuario_id})")
            print(f"        📅 Creada: {created_at[:10] if created_at else 'N/A'}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # =====================================================
    # 6. TABLA RESEÑAS
    # =====================================================
    print_header("RESEÑAS")
    try:
        result = client.table("resenas").select("*, lugares(nombre)").execute()
        resenas = result.data if result.data else []
        
        print(f"\n   Total: {len(resenas)} reseñas")
        
        # Rating promedio
        ratings = [r.get('rating', 0) for r in resenas if r.get('rating')]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            print(f"\n   ⭐ Rating promedio: {avg_rating:.1f}/5")
        
        # Últimas reseñas
        print(f"\n   📝 Últimas reseñas:")
        for resena in resenas[-5:]:
            rating = resena.get('rating', 'N/A')
            comentario = resena.get('comentario', '')[:50]
            lugar = resena.get('lugares', {}).get('nombre', 'N/A')
            print(f"      • {lugar}: ⭐ {rating} - \"{comentario}...\"")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # =====================================================
    # 7. TABLA FAVORITOS
    # =====================================================
    print_header("FAVORITOS")
    try:
        result = client.table("favoritos").select("count", count="exact").execute()
        total_favoritos = getattr(result, 'count', 0)
        
        print(f"\n   Total: {total_favoritos} favoritos")
        
        # Top lugares favoritos
        result = client.table("favoritos").select("lugar_id, count", count="exact").group_by("lugar_id").order("count", desc=True).limit(5).execute()
        # Nota: group_by puede no funcionar en todas las versiones de Supabase
        print(f"\n   ❤️ Lugares más guardados:")
        # Simplificado: mostrar estadística básica
        
    except Exception as e:
        print(f"   ℹ️ No se pudieron obtener estadísticas de favoritos")
    
    # =====================================================
    # 8. ESTADÍSTICAS GLOBALES
    # =====================================================
    print_header("ESTADÍSTICAS GLOBALES")
    
    stats = {}
    tables = ["lugares", "eventos", "usuarios", "rutas_usuario", "resenas"]
    
    for table in tables:
        try:
            result = client.table(table).select("id", count="exact").limit(0).execute()
            stats[table] = getattr(result, 'count', 0)
        except:
            stats[table] = "N/A"
    
    print(f"\n   📊 Resumen de datos:")
    print(f"      • Lugares turísticos: {stats.get('lugares', 0)}")
    print(f"      • Eventos: {stats.get('eventos', 0)}")
    print(f"      • Usuarios registrados: {stats.get('usuarios', 0)}")
    print(f"      • Rutas guardadas: {stats.get('rutas_usuario', 0)}")
    print(f"      • Reseñas escritas: {stats.get('resenas', 0)}")
    
    # =====================================================
    # 9. ÚLTIMA ACTUALIZACIÓN
    # =====================================================
    print_header("INFORMACIÓN")
    print(f"\n   📍 Supabase URL: {os.getenv('SUPABASE_URL', 'No configurada')[:40]}...")
    print(f"   🔐 API Key: {'✅ Configurada' if os.getenv('SUPABASE_KEY') else '❌ No configurada'}")
    print(f"   🔑 Service Role Key: {'✅ Configurada' if os.getenv('SUPABASE_SERVICE_KEY') else '❌ No configurada'}")
    
    print_separator()
    print("   ✅ Script completado")
    print_separator()


if __name__ == "__main__":
    main()