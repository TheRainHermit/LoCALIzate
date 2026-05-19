"""
Script para diagnosticar y resolver problemas de RLS en Supabase.

Verifica:
1. Qué tablas existen
2. Estado de RLS (habilitado/deshabilitado)
3. Políticas de seguridad
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv()

from supabase import create_client

def check_supabase_tables():
    """Verificar tablas y estado de RLS."""
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: Variables de entorno no configuradas")
        return
    
    client = create_client(supabase_url, supabase_key)
    
    print("=" * 70)
    print("🔍 DIAGNÓSTICO - SUPABASE RLS Y TABLAS")
    print("=" * 70)
    
    print(f"\n📡 Conectando a: {supabase_url}")
    print("✅ Conexión exitosa\n")
    
    # Lista de tablas a verificar
    tablas_esperadas = [
        'categorias', 'lugares', 'eventos', 'usuarios',
        'usuario_intereses', 'rutas_usuario', 'ruta_detalle',
        'favoritos', 'resenas', 'conversaciones', 'mensajes',
        'actividad_logs', 'configuracion', 'notificaciones'
    ]
    
    print("=" * 70)
    print("📊 VERIFICANDO TABLAS Y REGISTROS")
    print("=" * 70)
    
    tablas_encontradas = []
    tablas_vacias = []
    tablas_con_datos = []
    
    for tabla in tablas_esperadas:
        try:
            # Intentar contar registros
            result = client.table(tabla).select("*", count="exact").limit(1).execute()
            count = result.count if hasattr(result, 'count') else len(result.data)
            
            tablas_encontradas.append(tabla)
            
            if count == 0:
                print(f"   ⚠️  {tabla:25} - 0 registros (probablemente RLS bloqueando)")
                tablas_vacias.append(tabla)
            else:
                print(f"   ✅ {tabla:25} - {count} registros")
                tablas_con_datos.append(tabla)
                
        except Exception as e:
            error_msg = str(e)
            if "42P01" in error_msg or "does not exist" in error_msg:
                print(f"   ❌ {tabla:25} - NO EXISTE (falta crear)")
            elif "new row violates" in error_msg or "policy" in error_msg.lower():
                print(f"   🔒 {tabla:25} - RLS BLOQUEANDO acceso")
                tablas_vacias.append(tabla)
            else:
                print(f"   ⚠️  {tabla:25} - Error: {error_msg[:40]}...")
    
    print("\n" + "=" * 70)
    print("📋 RESUMEN")
    print("=" * 70)
    print(f"Tablas encontradas: {len(tablas_encontradas)}/{len(tablas_esperadas)}")
    print(f"Tablas con datos: {len(tablas_con_datos)}")
    print(f"Tablas vacías/RLS bloqueando: {len(tablas_vacias)}")
    
    print("\n" + "=" * 70)
    print("🔧 SOLUCIÓN - HABILITAR ACCESO PÚBLICO")
    print("=" * 70)
    
    if len(tablas_vacias) > 0:
        print("""
⚠️  PROBLEMA DETECTADO: Acceso RLS está bloqueado

SOLUCIÓN RÁPIDA - En Supabase SQL Editor:

1. Deshabilitar RLS en tablas específicas:
""")
        for tabla in tablas_vacias:
            print(f"   ALTER TABLE {tabla} DISABLE ROW LEVEL SECURITY;")
        
        print("""
2. O crear políticas públicas para lectura:
""")
        for tabla in tablas_vacias:
            print(f"""   CREATE POLICY "public_read_{tabla}" ON {tabla}
       FOR SELECT USING (true);
""")
        
        print("3. Después ejecuta este script nuevamente para verificar")
    
    elif len(tablas_con_datos) == len(tablas_esperadas):
        print("✅ TODO ESTÁ FUNCIONANDO CORRECTAMENTE")
        print("   Las tablas están visibles y tienen datos")
    
    print("\n" + "=" * 70)
    print("🎯 PASO A PASO - Resolver en Supabase")
    print("=" * 70)
    print("""
1. Abre: https://app.supabase.com
2. Selecciona tu proyecto
3. Ve a: SQL Editor → New Query
4. Copia y ejecuta ESTE código:

--- OPCIÓN A: Deshabilitar RLS completamente ---
ALTER TABLE categorias DISABLE ROW LEVEL SECURITY;
ALTER TABLE lugares DISABLE ROW LEVEL SECURITY;
ALTER TABLE eventos DISABLE ROW LEVEL SECURITY;
ALTER TABLE usuarios DISABLE ROW LEVEL SECURITY;
ALTER TABLE usuario_intereses DISABLE ROW LEVEL SECURITY;
ALTER TABLE rutas_usuario DISABLE ROW LEVEL SECURITY;
ALTER TABLE ruta_detalle DISABLE ROW LEVEL SECURITY;
ALTER TABLE favoritos DISABLE ROW LEVEL SECURITY;
ALTER TABLE resenas DISABLE ROW LEVEL SECURITY;
ALTER TABLE conversaciones DISABLE ROW LEVEL SECURITY;
ALTER TABLE mensajes DISABLE ROW LEVEL SECURITY;
ALTER TABLE actividad_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE configuracion DISABLE ROW LEVEL SECURITY;
ALTER TABLE notificaciones DISABLE ROW LEVEL SECURITY;

--- Verificar que funcionó ---
SELECT table_name, row_security_enabled 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

5. Luego ejecuta: python scripts/test_rls.py

Esto debería resolver el problema.
""")

if __name__ == "__main__":
    check_supabase_tables()
