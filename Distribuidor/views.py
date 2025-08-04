from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ChibchaWeb.decorators import distribuidor_required

@login_required
@distribuidor_required
def dashboard_distribuidor(request):
    cliente = request.user.cliente
    return render(request, 'distribuidores/dashboard.html', {'cliente': cliente}) 

@distribuidor_required
def mis_paquetes(request):
    cliente = request.cliente
    return render(request, 'distribuidores/mis_paquetes.html', {'cliente': cliente})