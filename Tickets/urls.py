from django.urls import path
from .views import crear_ticket, tickets_cliente
from Empleados.views import SupervisorDashboardView

app_name = 'tickets'

urlpatterns = [
    path('nuevo/', crear_ticket, name='crear_ticket'),
    path('cliente/', tickets_cliente, name='tickets_cliente'),
    path('supervisor/asignados/', SupervisorDashboardView.as_view(), name='tickets_asignados_supervisor'),
]