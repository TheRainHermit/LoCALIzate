import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"Conectando a: {url}")
client = create_client(url, key)

# Probar categorías
result = client.table("categorias").select("*", count="exact").execute()
print(f"Categorías: {len(result.data)} registros")

# Probar lugares
result = client.table("lugares").select("*", count="exact").execute()
print(f"Lugares: {len(result.data)} registros")