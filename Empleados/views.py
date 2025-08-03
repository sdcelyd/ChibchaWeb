from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from ChibchaWeb.decorators import empleado_required, supervisor_required, agente_required
from .models import Empleado


class EmpleadoLoginView(LoginView):
    template_name = 'logEmpleados.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Añadir clases CSS a los campos del formulario
        form.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ingresa tu usuario'})
        form.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ingresa tu contraseña'})
        return form
    
    def form_valid(self, form):
        # Verificar que el usuario que se logea sea un empleado activo
        user = form.get_user()
        try:
            empleado = user.empleado
            if not empleado.activo:
                messages.error(self.request, 'Tu cuenta de empleado está desactivada.')
                return self.form_invalid(form)
            
            # Login exitoso, redirigir según el rol
            response = super().form_valid(form)
            if empleado.rol == 'supervisor':
                return redirect('empleados:supervisor_dashboard')
            else:  # agente
                return redirect('empleados:agente_dashboard')
        except Empleado.DoesNotExist:
            messages.error(self.request, 'Este usuario no es un empleado válido.')
            return self.form_invalid(form)
            return self.form_invalid(form)
    
    def get_success_url(self):
        return '/empleados/dashboard/'


@method_decorator(empleado_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'
    
    def get(self, request, *args, **kwargs):
        # Redirigir según el rol del empleado
        empleado = request.user.empleado
        if empleado.rol == 'supervisor':
            return redirect('empleados:supervisor_dashboard')
        else:
            return redirect('empleados:agente_dashboard')


@method_decorator(supervisor_required, name='dispatch')
class SupervisorDashboardView(TemplateView):
    template_name = 'supervisor_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supervisor = self.request.user.empleado
        
        # Filtrar agentes del mismo nivel que el supervisor
        agentes_mismo_nivel = Empleado.objects.filter(
            rol='agente',
            nivel=supervisor.nivel,
            activo=True
        ).select_related('user')
        
        context['empleado'] = supervisor
        context['agentes'] = agentes_mismo_nivel
        context['nivel_supervisor'] = supervisor.nivel
        
        # TODO: Agregar tickets del mismo nivel cuando se cree la tabla Ticket
        # tickets_nivel = Ticket.objects.filter(nivel=supervisor.nivel)
        # context['tickets'] = tickets_nivel
        
        return context


@method_decorator(agente_required, name='dispatch')
class AgenteDashboardView(TemplateView):
    template_name = 'agente_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agente = self.request.user.empleado
        
        # TODO: Implementar cuando se cree la tabla Ticket
        # tickets_solucionados = Ticket.objects.filter(agente=agente, estado='resuelto')
        # tickets_pendientes = Ticket.objects.filter(agente=agente, estado__in=['pendiente', 'en_proceso'])
        # context['tickets_solucionados'] = tickets_solucionados
        # context['tickets_pendientes'] = tickets_pendientes
        
        context['empleado'] = agente
        context['usuario'] = agente.user
        
        # Estadísticas simuladas para mostrar estructura
        context['stats'] = {
            'tickets_solucionados_count': 0,  # tickets_solucionados.count()
            'tickets_pendientes_count': 0,    # tickets_pendientes.count()
            'tickets_hoy': 0,                 # tickets resueltos hoy
            'calificacion_promedio': 0        # promedio de calificaciones
        }
        
        return context


class EmpleadoLogoutView(LogoutView):
    next_page = 'empleados:log'
