
from functools import wraps
from pyexpat.errors import messages

from django.shortcuts import redirect


def administrador_required(view_func):
    """
    Decorador que verifica que el usuario sea un Administrador autenticado
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('administradores:login')
        
        try:
            from Administradores.models import Administrador
            administrador = Administrador.objects.get(user=request.user)
            
            if not administrador.activo:
                messages.error(request, "Tu cuenta de administrador está desactivada.")
                return redirect('administradores:login')
            
            # Actualizar último acceso
            from django.utils import timezone
            administrador.ultimo_acceso = timezone.now()
            administrador.save()
            
            request.administrador = administrador
            return view_func(request, *args, **kwargs)
        except Administrador.DoesNotExist:
            messages.error(request, "No tienes permisos de administrador para acceder a esta página.")
            return redirect('administradores:login')
    
    return wrapper


def admin_permission_required(permission_field):
    """
    Decorador que verifica permisos específicos del administrador
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Primero verificar que sea administrador
            admin_wrapper = administrador_required(view_func)
            response = admin_wrapper(request, *args, **kwargs)
            
            # Si no es una respuesta de redirección, verificar permisos específicos
            if hasattr(request, 'administrador'):
                if not getattr(request.administrador, permission_field, False):
                    messages.error(request, "No tienes permisos suficientes para realizar esta acción.")
                    return redirect('administradores:dashboard')
            
            return response
        return wrapper
    return decorator