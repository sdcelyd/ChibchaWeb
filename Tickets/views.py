# Tickets/views.py

from django.shortcuts import render, redirect
from .forms import TicketForm
from .models import Ticket, HistoriaTicket
from ChibchaWeb.decorators import cliente_required, supervisor_required
from django.utils import timezone
from django.utils.decorators import method_decorator


@cliente_required
def crear_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.cliente = request.cliente
            ticket.fechar_creacion = timezone.now().date()
            ticket.save()
            return redirect('tickets:mis_tickets')  # o a la vista de tickets del cliente
    else:
        form = TicketForm()

    return render(request, 'tickets/crear_ticket.html', {'form': form})


@cliente_required
def mis_tickets(request):
    cliente = request.cliente
    tickets = Ticket.objects.filter(cliente=cliente).order_by('-fechar_creacion')
    return render(request, 'tickets/mis_tickets.html', {'tickets': tickets})

def obtener_estado_actual(self):
    ultima = self.historial.order_by('-fecha_modificacion').first()
    return ultima.estado.nombreEstado if ultima and ultima.estado else 'Sin estado'