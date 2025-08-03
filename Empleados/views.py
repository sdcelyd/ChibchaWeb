from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from ChibchaWeb.decorators import empleado_required, supervisor_required, agente_required
from .models import Empleado


class EmpleadoLoginView(LoginView):
    template_name = 'empleados/login.html'
    
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
    
    def get_success_url(self):
        return '/empleados/dashboard/'


@method_decorator(empleado_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'empleados/dashboard.html'
    
    def get(self, request, *args, **kwargs):
        # Redirigir según el rol del empleado
        empleado = request.user.empleado
        if empleado.rol == 'supervisor':
            return redirect('empleados:supervisor_dashboard')
        else:
            return redirect('empleados:agente_dashboard')


@method_decorator(supervisor_required, name='dispatch')
class SupervisorDashboardView(TemplateView):
    template_name = 'empleados/supervisor_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empleado'] = self.request.user.empleado
        # Aquí puedes agregar más datos específicos del supervisor
        return context


@method_decorator(agente_required, name='dispatch')
class AgenteDashboardView(TemplateView):
    template_name = 'empleados/agente_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empleado'] = self.request.user.empleado
        # Aquí puedes agregar más datos específicos del agente
        return context


class EmpleadoLogoutView(LogoutView):
    next_page = 'empleados:login'
