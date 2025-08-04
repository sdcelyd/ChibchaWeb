# Tickets/views.py

from django.shortcuts import render, redirect
from .forms import TicketForm
from .models import Ticket, HistoriaTicket
from ChibchaWeb.decorators import cliente_required, supervisor_required
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from Empleados.models import Empleado

@method_decorator(supervisor_required, name='dispatch')
class DashboardSupervisorView(TemplateView):
    template_name = 'supervisor_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supervisor = self.request.empleado  # ← cambio aquí
        nivel = supervisor.nivel

        agentes_nivel = Empleado.objects.filter(nivel=nivel, rol='tecnico')

        tickets_asignados = HistoriaTicket.objects.filter(
            empleado_id=supervisor.id
        ).select_related('ticket', 'estado')

        context['nivel_supervisor'] = nivel
        context['agentes'] = agentes_nivel
        context['tickets_asignados'] = tickets_asignados

        print("Supervisor ID:", supervisor.id)
        print("HistoriaTicket empleados:", HistoriaTicket.objects.values_list('empleado_id', flat=True))
        return context


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