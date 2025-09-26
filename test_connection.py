import psycopg2
from urllib.parse import urlparse

# Tu nueva URL correcta
DATABASE_URL = "postgresql://soltech_user:GDP2N2pwUhcxHP2nFXdXiDtMdF20HotZ@dpg-d327q8i4d50c73absg00-a.oregon-postgres.render.com/soltech"

print("🔍 Probando conexión a la base de datos...")
print(f"📋 URL: {DATABASE_URL}")

try:
    # Parsear la URL
    result = urlparse(DATABASE_URL)
    
    print(f"🌐 Host: {result.hostname}")
    print(f"🚪 Puerto: {result.port or '5432 (default)'}")
    print(f"📊 Base de datos: {result.path[1:]}")
    print(f"👤 Usuario: {result.username}")
    
    # Intentar conexión
    conn = psycopg2.connect(
        dbname=result.path[1:],  # remover el slash inicial
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port or 5432,  # usar puerto por defecto si no está especificado
        sslmode='require'
    )
    
    print("✅ ¡CONEXIÓN EXITOSA!")
    
    # Verificar información de la base de datos
    cursor = conn.cursor()
    
    # Verificar tablas existentes
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    
    print(f"📋 Tablas existentes: {len(tables)}")
    if tables:
        print("   - " + "\n   - ".join([table[0] for table in tables]))
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    print("\n🔧 Soluciones sugeridas:")
    print("1. Verifica tu conexión a internet")
    print("2. Prueba con una VPN (puede haber bloqueos regionales)")
    print("3. Verifica que la base de datos esté activa en Render")
    print("4. Contacta a Render support si el problema persiste")