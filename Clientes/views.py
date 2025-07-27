def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    return render(request, 'detalle_cliente.html', {'cliente': cliente})
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Cliente
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

from .forms import ClienteForm
from django.views.decorators.http import require_POST


def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clientes:registro_exitoso')
    else:
        form = ClienteForm()

    return render(request, 'clientes/registro.html', {'form': form})

def cliente_login(request):
    if request.method == 'POST':
        nickname = request.POST.get('username')
        contrasena = request.POST.get('password')
        user = authenticate(request, username=nickname, password=contrasena)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirige a la página de inicio o dashboard
        else:
            return HttpResponse("Credenciales inválidas. Por favor, inténtalo de nuevo.", status=401)
    return render(request, 'clientes/login.html')


@require_POST #para que cualquiera no pueda borrar con solo ingresar una url
def borrar_cliente(request, cliente_id):
    if request.method == 'POST':
        cliente = get_object_or_404(Cliente, id=cliente_id)
        cliente.delete()
        return JsonResponse({'mensaje': 'Cliente eliminado correctamente'}, status=200)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
from django.shortcuts import render, get_object_or_404, redirect
from .models import Cliente


def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == 'POST':
        cliente.nombre = request.POST.get('nombre')
        cliente.apellido = request.POST.get('apellido')
        cliente.email = request.POST.get('email')
        cliente.telefono = request.POST.get('telefono')
        cliente.save()
        return redirect('/Clientes/exito/')  # O donde quieras redirigir

    return render(request, 'clientes/editar.html', {'cliente': cliente})
