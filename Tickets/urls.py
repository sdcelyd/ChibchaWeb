# Tickets/urls.py

from django.urls import path
from .views import crear_ticket, mis_tickets

app_name = 'tickets'

urlpatterns = [
    path('nuevo/', crear_ticket, name='crear_ticket'),
    path('mios/', mis_tickets, name='mis_tickets'),
]