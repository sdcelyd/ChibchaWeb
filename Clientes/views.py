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
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils.http import urlsafe_base64_decode




@cliente_required
def home_cliente(request):
    cliente = request.cliente
    return render(request, 'home_clientes.html', {'cliente': cliente})

def registrar_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crear token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # Construir URL de activación
            activation_link = request.build_absolute_uri(
                reverse('clientes:activar_cuenta', kwargs={'uidb64': uid, 'token': token})
            )
            # Enviar correo
            send_mail(
                subject='Activa tu cuenta',
                message=f'Hola {user.first_name}, activa tu cuenta haciendo clic en el siguiente enlace: {activation_link}',
                from_email='no-reply@tusitio.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
            return redirect('clientes:registro_exitoso')  # Puedes mostrar un mensaje tipo: "Revisa tu correo"
    else:
        form = RegistroClienteForm()

    return render(request, 'registro.html', {'form': form})

def activar_cuenta(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'activacion_exitosa.html')
    else:
        return render(request, 'activacion_fallida.html')


def registro_exitoso(request):
    return render(request, 'exito.html')  

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
    cliente = request.cliente
    if not cliente.suscripcion_activa:
        messages.warning(request, "Necesitas una suscripción activa para acceder a tus hosts.")
        return redirect('clientes:home_clientes')
    
    # Obtener SOLO los dominios del plan de hosting (no los del distribuidor)
    from Dominios.models import Dominios
    dominios = Dominios.objects.filter(clienteId=cliente, compraDistribuidor=False)
    
    return render(request, 'mis_hosts.html', {
        'cliente': cliente,
        'dominios': dominios
    })  

@cliente_required
def editar_cliente(request, cliente_id):
    cliente = request.cliente  # Usar el cliente del decorador
    
    # Verificar que el cliente solo pueda editar su propio perfil
    if cliente.id != cliente_id:
        messages.error(request, "No puedes editar el perfil de otro cliente.")
        return redirect('clientes:detalle_cliente')

    if request.method == 'POST':
        from django.contrib.auth.models import User
        
        new_username = request.POST.get('username', '').strip()
        new_email = request.POST.get('email', '').strip()
        
        # Validar que los campos requeridos no estén vacíos
        if not new_username:
            messages.error(request, "El nombre de usuario es obligatorio.")
            return render(request, 'editar.html', {'cliente': cliente})
            
        if not new_email:
            messages.error(request, "El email es obligatorio.")
            return render(request, 'editar.html', {'cliente': cliente})
        
        # Verificar si el nombre de usuario ya existe (excluyendo el usuario actual)
        if new_username != cliente.user.username:
            if User.objects.filter(username=new_username).exists():
                messages.error(request, f"El nombre de usuario '{new_username}' ya está en uso. Por favor elige otro.")
                return render(request, 'editar.html', {'cliente': cliente})
        
        # Verificar si el email ya existe (excluyendo el usuario actual)
        if new_email != cliente.user.email:
            if User.objects.filter(email=new_email).exists():
                messages.error(request, f"El email '{new_email}' ya está en uso. Por favor elige otro.")
                return render(request, 'editar.html', {'cliente': cliente})
        
        try:
            # Actualizar campos del User
            cliente.user.username = new_username
            cliente.user.first_name = request.POST.get('first_name', '').strip()
            cliente.user.last_name = request.POST.get('last_name', '').strip()
            cliente.user.email = new_email
            
            # Actualizar contraseña si se proporcionó
            new_password = request.POST.get('password', '').strip()
            if new_password:
                if len(new_password) < 8:
                    messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
                    return render(request, 'editar.html', {'cliente': cliente})
                    
                cliente.user.set_password(new_password)
                # Mantener la sesión activa después del cambio de contraseña
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, cliente.user)
                messages.info(request, "Tu contraseña ha sido actualizada correctamente.")
            
            cliente.user.save()
            
            # Actualizar campos del Cliente
            cliente.telefono = request.POST.get('telefono', '').strip()
            cliente.save()
            
            messages.success(request, "¡Perfil actualizado exitosamente!")
            return redirect('clientes:perfil')
            
        except Exception as e:
            messages.error(request, f"Error al actualizar el perfil: {str(e)}")
            return render(request, 'editar.html', {'cliente': cliente})

    return render(request, 'editar.html', {'cliente': cliente})

@cliente_required
def quiero_ser_distribuidor(request):
    cliente = request.cliente
    return render(request, 'quiero_ser_distribuidor.html', {'cliente': cliente})

@cliente_required
def hacer_distribuidor(request):
    if request.method == 'POST':
        cliente = request.cliente  # Usar el cliente del decorador
        
        # Verificar que tenga suscripción activa antes de hacerlo distribuidor
        if not cliente.suscripcion_activa:
            messages.error(request, "Necesitas una suscripción activa para convertirte en distribuidor.")
            return redirect('clientes:quiero_ser_distribuidor')
            
        if not cliente.es_distribuidor:
            cliente.es_distribuidor = True
            cliente.save()  # Aquí se dispara la señal
            messages.success(request, "¡Felicidades! Ahora eres distribuidor de ChibchaWeb.")
        return redirect('clientes:distribuidor_exito')  
    return redirect('clientes:quiero_ser_distribuidor')  

@cliente_required
def distribuidor_exito(request):
    cliente = request.cliente
    return render(request, 'distribuidor_exito.html', {'cliente': cliente})