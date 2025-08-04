# Tickets/urls.py

from django.urls import path
from .views import crear_ticket, mis_tickets
from Empleados.views import SupervisorDashboardView

app_name = 'tickets'

urlpatterns = [
    path('nuevo/', crear_ticket, name='crear_ticket'),
    path('mios/', mis_tickets, name='mis_tickets'),
    path('supervisor/asignados/', SupervisorDashboardView.as_view(), name='tickets_asignados_supervisor'),
]