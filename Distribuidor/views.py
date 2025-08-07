from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ChibchaWeb.decorators import distribuidor_required
from Pagos.models import PagoDistribuidor

@login_required
@distribuidor_required
def dashboard_distribuidor(request):
    cliente = request.user.cliente
    distribuidor = cliente.perfil_distribuidor  # accede al perfil distribuidor
    
    # Estadísticas adicionales
    pagos_paquetes = PagoDistribuidor.objects.filter(cliente=cliente)
    total_invertido = sum(pago.monto for pago in pagos_paquetes)
    
    # Obtener dominios creados con espacios del distribuidor
    from Dominios.models import Dominios
    dominios_distribuidor = Dominios.objects.filter(clienteId=cliente, compraDistribuidor=True)

    context = {
        'cliente': cliente,
        'distribuidor': distribuidor,
        'total_invertido': total_invertido,
        'total_pagos': pagos_paquetes.count(),
        'dominios_distribuidor': dominios_distribuidor,
    }
    return render(request, 'distribuidores/dashboard.html', context)

@distribuidor_required
def mis_paquetes(request):
    cliente = request.cliente
    distribuidor = cliente.perfil_distribuidor
    
    # Obtener los pagos de paquetes realizados por el distribuidor
    pagos_paquetes = PagoDistribuidor.objects.filter(cliente=cliente).order_by('-fecha')
    
    # Obtener los dominios creados con espacios del distribuidor
    from Dominios.models import Dominios
    dominios_distribuidor = Dominios.objects.filter(clienteId=cliente, compraDistribuidor=True)
    
    context = {
        'cliente': cliente,
        'distribuidor': distribuidor,
        'pagos_paquetes': pagos_paquetes,
        'dominios_distribuidor': dominios_distribuidor,
    }
    return render(request, 'distribuidores/mis_paquetes.html', context)
