from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Cliente
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import RegistroClienteForm
from django.contrib.auth import logout
from django.contrib import messages
from .forms import ClienteForm
from django.views.decorators.http import require_POST
from ChibchaWeb.decorators import cliente_required


def registrar_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clientes:registro_exitoso')  # Asegúrate de tener esta ruta en urls.py
    else:
        form = RegistroClienteForm()

    return render(request, 'registro.html', {'form': form})

@cliente_required
def detalle_cliente(request):
    # request.cliente ya está disponible automáticamente
    cliente = request.cliente
    return render(request, 'detalle_cliente.html', {'cliente': cliente})

@login_required
def perfil(request):
    cliente = Cliente.objects.get(user=request.user)
    return render(request, 'perfil.html', {'cliente': cliente})

@require_POST
@cliente_required
def borrar_cliente(request):
    if request.method == 'POST':
        try:
            cliente = request.cliente  # Usar el cliente del decorador
            user = request.user
            cliente.delete()   # Elimina el registro de Cliente
            user.delete()      # Elimina el usuario de Django
            messages.success(request, "Tu cuenta fue eliminada exitosamente.")
            logout(request)    # Cierra sesión
            
        except Exception as e:
            messages.error(request, f"Error al eliminar la cuenta: {str(e)}")

    return redirect('home')

@cliente_required
def mis_hosts(request):
    return render(request, 'mis_hosts.html')  

@cliente_required
def editar_cliente(request, cliente_id):
    cliente = request.cliente  # Usar el cliente del decorador
    
    # Verificar que el cliente solo pueda editar su propio perfil
    if cliente.id != cliente_id:
        messages.error(request, "No puedes editar el perfil de otro cliente.")
        return redirect('clientes:detalle_cliente')

    if request.method == 'POST':
        # Actualizar campos del User
        cliente.user.username = request.POST.get('username', cliente.user.username)
        cliente.user.first_name = request.POST.get('first_name', cliente.user.first_name)
        cliente.user.last_name = request.POST.get('last_name', cliente.user.last_name)
        cliente.user.email = request.POST.get('email', cliente.user.email)
        
        # Actualizar contraseña si se proporcionó
        new_password = request.POST.get('password')
        if new_password:
            cliente.user.set_password(new_password)
            # Mantener la sesión activa después del cambio de contraseña
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, cliente.user)
        
        cliente.user.save()
        
        # Actualizar campos del Cliente
        cliente.telefono = request.POST.get('telefono', cliente.telefono)
        cliente.save()
        
        messages.success(request, "Perfil actualizado exitosamente.")
        return redirect('clientes:detalle_cliente')

    return render(request, 'editar.html', {'cliente': cliente})