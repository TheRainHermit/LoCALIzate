# Migrations Versions Directory

Este directorio contiene los archivos de migración generados por Alembic.

## Para crear una nueva migración:

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Generar migración automática (detecta cambios en modelos)
alembic revision --autogenerate -m "descripcion_del_cambio"

# Generar migración vacía (manual)
alembic revision -m "descripcion_del_cambio"