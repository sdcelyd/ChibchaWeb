from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Cliente
from django.http import HttpResponse
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .forms import RegistroClienteForm
from django.contrib.auth import logout
from django.contrib import messages


from .forms import ClienteForm
from django.views.decorators.http import require_POST


def registrar_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clientes:registro_exitoso')  # Asegúrate de tener esta ruta en urls.py
    else:
        form = RegistroClienteForm()

    return render(request, 'clientes/registro.html', {'form': form})

@login_required
def detalle_cliente(request):
    cliente = Cliente.objects.get(user=request.user)
    return render(request, 'clientes/detalle_cliente.html', {'cliente': cliente})


@require_POST
@login_required
def borrar_cliente(request):
    if request.method == 'POST':
        try:
            cliente = Cliente.objects.get(user=request.user)
            user = request.user
            cliente.delete()   # Elimina el registro de Cliente
            user.delete()      # Elimina el usuario de Django
            messages.success(request, "Tu cuenta fue eliminada exitosamente.")
            logout(request)    # Cierra sesión
            
        except Cliente.DoesNotExist:
            pass  # Silenciosamente ignora si no existe

    return redirect('home')  # Ajusta a la ruta de tu página principal



def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

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
        
        cliente.user.save()
        
        # Actualizar campos del Cliente
        cliente.telefono = request.POST.get('telefono', cliente.telefono)
        cliente.save()
        
        return redirect('clientes:detalle_cliente')

    return render(request, 'clientes/editar.html', {'cliente': cliente})

class ClienteLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('clientes:exitologin')  # a donde lo lleva si es exitoso
    redirect_authenticated_user = True

@login_required
def vista_exito(request):
    return render(request, 'clientes/exito.html')

@login_required
def mis_hosts(request):
    return render(request, 'mis_hosts.html')  