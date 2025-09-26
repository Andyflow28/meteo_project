import psycopg2

def check_table_structure():
    try:
        conn = psycopg2.connect(
            dbname='soltech',
            user='soltech_user',
            password='GDP2N2pwUhcxHP2nFXdXiDtMdF20HotZ',
            host='dpg-d327q8i4d50c73absg00-a.oregon-postgres.render.com',
            port=5432,
            sslmode='require'
        )
        
        cursor = conn.cursor()
        
        # Verificar estructura de la tabla users
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position
        """)
        
        print("📋 Estructura actual de la tabla 'users':")
        for col in cursor.fetchall():
            print(f"   - {col[0]}: {col[1]} (nullable: {col[2]})")
        
        # Verificar si existe la tabla django_migrations
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'django_migrations'
        """)
        
        if cursor.fetchone():
            print("✅ La tabla django_migrations existe")
        else:
            print("❌ La tabla django_migrations NO existe")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_table_structure()