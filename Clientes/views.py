from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Cliente
from .forms import ClienteForm
from django.views.decorators.http import require_POST

def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registro_exitoso')
    else:
        form = ClienteForm()

    return render(request, 'clientes/registro.html', {'form': form})


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