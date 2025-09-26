import psycopg2

def fix_database():
    print("🔧 Agregando columnas faltantes a la tabla users...")
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(
            dbname='soltech',
            user='soltech_user',
            password='GDP2N2pwUhcxHP2nFXdXiDtMdF20HotZ',
            host='dpg-d327q8i4d50c73absg00-a.oregon-postgres.render.com',
            port=5432,
            sslmode='require'
        )
        
        cursor = conn.cursor()
        
        # Columnas que necesitamos agregar
        columns_to_add = [
            ('is_staff', 'BOOLEAN DEFAULT FALSE'),
            ('is_superuser', 'BOOLEAN DEFAULT FALSE'),
            ('is_active', 'BOOLEAN DEFAULT TRUE'),
            ('date_joined', 'TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP'),
            ('last_login', 'TIMESTAMP WITH TIME ZONE NULL')
        ]
        
        for column_name, column_def in columns_to_add:
            try:
                # Verificar si la columna ya existe
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='{column_name}'
                """)
                exists = cursor.fetchone()
                
                if not exists:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
                    print(f"✅ Columna '{column_name}' agregada exitosamente")
                else:
                    print(f"ℹ️  Columna '{column_name}' ya existe")
                    
            except Exception as e:
                print(f"⚠️  Error con columna '{column_name}': {e}")
        
        conn.commit()
        
        # Verificar la estructura final
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position
        """)
        
        print("\n📋 Estructura final de la tabla 'users':")
        for col in cursor.fetchall():
            print(f"   - {col[0]}: {col[1]} (nullable: {col[2]})")
        
        conn.close()
        print("\n🎉 ¡Base de datos reparada! Ahora puedes crear el superusuario.")
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("💡 Verifica tu conexión a internet y las credenciales de la base de datos")

if __name__ == "__main__":
    fix_database()