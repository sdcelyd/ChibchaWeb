# Tickets/forms.py

from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['nombreTicket', 'descripcionTicket']
        labels = {
            'nombreTicket': 'Nombre del Ticket',
            'descripcionTicket': 'Descripción del problema',
        }
        widgets = {
            'nombreTicket': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto del ticket'}),
            'descripcionTicket': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe el problema'}),
        }
