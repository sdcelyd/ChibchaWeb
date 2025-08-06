# Tickets/views.py

from django.shortcuts import render, redirect
from .forms import TicketForm
from .models import Ticket, Estado, HistoriaTicket
from ChibchaWeb.decorators import cliente_required
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
            
            # Crear entrada inicial en HistoriaTicket con estado "En espera"
            estado_inicial, created = Estado.objects.get_or_create(
                nombreEstado='En espera',
                defaults={'idEstado': 1}
            )
            
            HistoriaTicket.objects.create(
                modDescripcion=f'Ticket creado por el cliente {request.user.get_full_name() or request.user.username}',
                fecha_modificacion=timezone.now().date(),
                empleado=None,  # Inicialmente sin asignar
                ticket=ticket,
                estado=estado_inicial
            )
            
            return redirect('tickets:tickets_cliente')
    else:
        form = TicketForm()

    return render(request, 'crear_ticket.html', {'form': form})


@cliente_required
def tickets_cliente(request):
    cliente = request.cliente
    tickets = Ticket.objects.filter(cliente=cliente).order_by('-fechar_creacion')
    return render(request, 'tickets_cliente.html', {'tickets': tickets})

def obtener_estado_actual(self):
    ultima = self.historial.order_by('-fecha_modificacion').first()
    return ultima.estado.nombreEstado if ultima and ultima.estado else 'Sin estado'