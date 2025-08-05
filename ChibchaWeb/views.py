from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from Clientes.models import Cliente
from .planes import PLANES_DISPONIBLES


def home(request):
    # Obtener estadísticas reales
    total_clientes = Cliente.objects.count()
    
    # Calcular sitios web aproximados (asumiendo promedio de 2-3 sitios por cliente)
    sitios_web_estimados = total_clientes * 2 if total_clientes > 0 else 0
    
    # Estadísticas para mostrar
    estadisticas = {
        'clientes': total_clientes,
        'sitios_web': int(sitios_web_estimados),
        'uptime': '99.99%',
        'tiempo_carga': '2.1s'
    }
    
    return render(request, 'informacion.html', {
        'planes': PLANES_DISPONIBLES,
        'estadisticas': estadisticas
    })

def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'lista_clientes.html', {'clientes': clientes})

def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    return render(request, 'detalle_cliente.html', {'cliente': cliente})

class ClienteLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        user = form.get_user()
        # Verificar que no sea un empleado
        if hasattr(user, 'empleado'):
            messages.error(self.request, 'Los empleados deben usar el portal de empleados.')
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'cliente'):
            if user.cliente.es_distribuidor:
                return reverse_lazy('distribuidores:dashboard')
            else:
                return reverse_lazy('clientes:perfil')
        return reverse_lazy('home')    

@login_required
def vista_exito(request):
    return render(request, 'exitologin.html')