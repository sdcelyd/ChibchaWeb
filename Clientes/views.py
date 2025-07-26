from django.shortcuts import render, redirect

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
