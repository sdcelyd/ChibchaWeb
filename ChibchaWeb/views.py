from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Clientes.models import Cliente


def home(request):
    return render(request, 'informacion.html')
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'lista_clientes.html', {'clientes': clientes})

def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    return render(request, 'detalle_cliente.html', {'cliente': cliente})

class ClienteLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('exitologin')  # a donde lo lleva si es exitoso
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        user = form.get_user()
        # Verificar que no sea un empleado
        if hasattr(user, 'empleado'):
            messages.error(self.request, 'Los empleados deben usar el portal de empleados.')
            return self.form_invalid(form)
        return super().form_valid(form)

@login_required
def vista_exito(request):
    return render(request, 'exitologin.html')