from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def register(request):
    if request.user.is_authenticated:
        return redirect('stations:dashboard')
        
    if request.method == 'POST':
        # Procesar registro manualmente
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        
        from .models import User
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name
            )
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido/a.')
            return redirect('stations:dashboard')
        except Exception as e:
            messages.error(request, f'Error en el registro: {str(e)}')
    
    return render(request, 'accounts/register.html')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('stations:dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido/a de nuevo, {user.full_name}!')
            return redirect('stations:dashboard')
        else:
            messages.error(request, 'Credenciales inválidas.')
    
    return render(request, 'accounts/login.html')

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')