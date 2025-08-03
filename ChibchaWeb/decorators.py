from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from Clientes.models import Cliente
from Empleados.models import Empleado


def cliente_required(view_func):
    """
    Decorador que verifica que el usuario sea un Cliente autenticado
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Primero verificar que esté autenticado
        if not request.user.is_authenticated:
            messages.warning(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('login')
        
        # Verificar que tenga perfil de Cliente
        try:
            cliente = Cliente.objects.get(user=request.user)
            # Agregar el cliente al request para uso en la vista
            request.cliente = cliente
            return view_func(request, *args, **kwargs)
        except Cliente.DoesNotExist:
            messages.error(request, "No tienes permisos de cliente para acceder a esta página.")
            return redirect('login')
    
    return wrapper


def empleado_required(view_func):
    """
    Decorador que verifica que el usuario sea un Empleado autenticado
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('empleados:login')
        
        try:
            empleado = Empleado.objects.get(user=request.user)
            if not empleado.activo:
                messages.error(request, "Tu cuenta de empleado está desactivada.")
                return redirect('empleados:login')
            
            request.empleado = empleado
            return view_func(request, *args, **kwargs)
        except Empleado.DoesNotExist:
            messages.error(request, "No tienes permisos de empleado para acceder a esta página.")
            return redirect('empleados:login')
    
    return wrapper


def supervisor_required(view_func):
    """
    Decorador que verifica que el usuario sea un Supervisor
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('empleados:login')
        
        try:
            empleado = Empleado.objects.get(user=request.user)
            if not empleado.activo:
                messages.error(request, "Tu cuenta de empleado está desactivada.")
                return redirect('empleados:login')
            
            if empleado.rol != 'supervisor':
                messages.error(request, "Solo supervisores pueden acceder a esta página.")
                return redirect('empleados:dashboard')
            
            request.empleado = empleado
            return view_func(request, *args, **kwargs)
        except Empleado.DoesNotExist:
            messages.error(request, "No tienes permisos de empleado para acceder a esta página.")
            return redirect('empleados:login')
    
    return wrapper


def agente_required(view_func):
    """
    Decorador que verifica que el usuario sea un Agente
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('empleados:login')
        
        try:
            empleado = Empleado.objects.get(user=request.user)
            if not empleado.activo:
                messages.error(request, "Tu cuenta de empleado está desactivada.")
                return redirect('empleados:login')
            
            if empleado.rol != 'agente':
                messages.error(request, "Solo agentes pueden acceder a esta página.")
                return redirect('empleados:dashboard')
            
            request.empleado = empleado
            return view_func(request, *args, **kwargs)
        except Empleado.DoesNotExist:
            messages.error(request, "No tienes permisos de empleado para acceder a esta página.")
            return redirect('empleados:login')
    
    return wrapper
