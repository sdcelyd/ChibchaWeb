from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from Clientes.models import Cliente


def home(request):
    return render(request, 'informacion.html')
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'lista_clientes.html', {'clientes': clientes})
def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    return render(request, 'detalle_cliente.html', {'cliente': cliente})