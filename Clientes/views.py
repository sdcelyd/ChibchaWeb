from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Cliente
from .forms import ClienteForm

def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registro_exitoso')
    else:
        form = ClienteForm()

    return render(request, 'clientes/registro.html', {'form': form})



def borrar_cliente(request, cliente_id):
    if request.method == 'POST':
        cliente = get_object_or_404(Cliente, id=cliente_id)
        cliente.delete()
        return JsonResponse({'mensaje': 'Cliente eliminado correctamente'}, status=200)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)