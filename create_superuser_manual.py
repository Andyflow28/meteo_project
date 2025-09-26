import os
import django
from django.contrib.auth.hashers import make_password

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meteo_project.settings')
django.setup()

from accounts.models import User

def create_superuser_manual():
    try:
        # Verificar si el usuario ya existe
        if User.objects.filter(email='joseguerreroaf@gmail.com').exists():
            print("⚠️  El usuario ya existe")
            return
        
        # Crear superusuario manualmente
        user = User.objects.create(
            email='joseguerreroaf@gmail.com',
            username='joseguerrero',
            full_name='Jose Guerrero',
            password=make_password('tu_contraseña_segura'),  # Cambia esta contraseña
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        
        print(f"✅ Superusuario creado exitosamente:")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   ID: {user.user_id}")
        
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")

if __name__ == "__main__":
    create_superuser_manual()