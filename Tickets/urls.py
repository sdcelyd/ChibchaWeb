# Tickets/urls.py

from django.urls import path
from .views import crear_ticket, mis_tickets, DashboardSupervisorView

app_name = 'tickets'

urlpatterns = [
    path('nuevo/', crear_ticket, name='crear_ticket'),
    path('mios/', mis_tickets, name='mis_tickets'),
    path('supervisor/asignados/', DashboardSupervisorView.as_view(), name='tickets_asignados_supervisor'),
]