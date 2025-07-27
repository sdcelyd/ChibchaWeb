from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

from .forms import ClienteForm

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
        nickname = request.POST.get('nickname')
        contrasena = request.POST.get('contrasena')
        user = authenticate(request, username=nickname, password=contrasena)
        if user is not None:
            login(request, user)
            return redirect('inicio')  # Redirige a la página de inicio o dashboard
        else:
            return HttpResponse("Credenciales inválidas. Por favor, inténtalo de nuevo.", status=401)
    return render(request, 'clientes/login.html')
