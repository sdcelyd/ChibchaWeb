from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.db.models import Q, Max
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.urls import reverse_lazy
from ChibchaWeb.decorators import empleado_required, supervisor_required, agente_required
from .models import Empleado
from Tickets.models import Ticket, Estado, HistoriaTicket


# Helper functions para eliminar código repetitivo
def obtener_tickets_asignados_empleado(empleado):
    """Obtiene los IDs de tickets asignados a un empleado específico"""
    return HistoriaTicket.objects.filter(
        empleado=empleado
    ).values_list('ticket__idTicket', flat=True).distinct()


def obtener_ultimo_estado_ticket(ticket):
    """Obtiene el último estado de un ticket específico"""
    return HistoriaTicket.objects.filter(
        ticket=ticket
    ).order_by('-fecha_modificacion', '-idCambioTicket').first()


def obtener_historial_ticket(ticket):
    """Obtiene el historial completo de un ticket"""
    return HistoriaTicket.objects.filter(
        ticket=ticket
    ).order_by('-fecha_modificacion').select_related('empleado__user', 'estado')


def procesar_tickets_con_estado(tickets_queryset):
    """Procesa una lista de tickets y obtiene su estado actual"""
    tickets_con_estado = []
    for ticket in tickets_queryset:
        ultimo_estado = obtener_ultimo_estado_ticket(ticket)
        
        tickets_con_estado.append({
            'ticket': ticket,
            'estado_actual': ultimo_estado.estado if ultimo_estado else None,
            'fecha_ultima_modificacion': ultimo_estado.fecha_modificacion if ultimo_estado else None
        })
    
    return tickets_con_estado


def procesar_tickets_para_agente(tickets_queryset, agente):
    """Procesa tickets específicamente para un agente con información adicional"""
    tickets_con_info = []
    for ticket in tickets_queryset:
        ultimo_estado = obtener_ultimo_estado_ticket(ticket)
        historial = obtener_historial_ticket(ticket)
        
        tickets_con_info.append({
            'ticket': ticket,
            'estado_actual': ultimo_estado.estado if ultimo_estado else None,
            'fecha_ultima_modificacion': ultimo_estado.fecha_modificacion if ultimo_estado else None,
            'historial': historial,
            'puede_resolver': ultimo_estado and ultimo_estado.estado.nombreEstado == 'En Proceso',
            'puede_escalar': ultimo_estado and ultimo_estado.estado.nombreEstado == 'En Proceso' and agente.nivel < 3
        })
    
    return tickets_con_info


def obtener_tickets_asignados_por_nivel(supervisor_nivel):
    """Obtiene información de tickets asignados a agentes del nivel del supervisor"""
    # Obtenemos la última entrada del historial para cada ticket que tenga un empleado asignado
    ultimas_historias = HistoriaTicket.objects.filter(
        empleado__isnull=False
    ).values('ticket__idTicket').annotate(
        ultima_fecha=Max('fecha_modificacion')
    )
    
    tickets_asignados_info = {}
    # Para cada ticket con una última entrada, verificamos si el empleado asignado es de este nivel
    for historia in ultimas_historias:
        ticket_id = historia['ticket__idTicket']
        ultima_fecha = historia['ultima_fecha']
        
        # Buscamos la entrada más reciente con esa fecha para ese ticket
        ultima_entrada = HistoriaTicket.objects.filter(
            ticket__idTicket=ticket_id,
            fecha_modificacion=ultima_fecha
        ).order_by('-idCambioTicket').first()
        
        if ultima_entrada and ultima_entrada.empleado and ultima_entrada.empleado.nivel == supervisor_nivel:
            tickets_asignados_info[ticket_id] = ultima_entrada
    
    return tickets_asignados_info


def obtener_tickets_sin_asignar_por_nivel(supervisor_nivel, tickets_asignados_ids):
    """Obtiene tickets sin asignar según el nivel del supervisor"""
    if supervisor_nivel == 1:
        # Para nivel 1: tickets no asignados y no escalados
        tickets_escalados_desde_este_nivel = HistoriaTicket.objects.filter(
            modDescripcion__contains=f'escalado del nivel {supervisor_nivel} al nivel'
        ).values_list('ticket__idTicket', flat=True).distinct()
        
        tickets_escalados_a_otros_niveles = HistoriaTicket.objects.filter(
            modDescripcion__contains='escalado al nivel'
        ).exclude(
            modDescripcion__contains='escalado al nivel 1'
        ).values_list('ticket__idTicket', flat=True).distinct()
        
        todos_tickets_escalados = set(tickets_escalados_desde_este_nivel) | set(tickets_escalados_a_otros_niveles)
        
        return Ticket.objects.exclude(
            idTicket__in=tickets_asignados_ids
        ).exclude(
            idTicket__in=list(todos_tickets_escalados)
        )
    else:
        # Para niveles superiores: tickets escalados a este nivel específico
        patron_escalamiento = f'al nivel {supervisor_nivel}'
        tickets_escalados = HistoriaTicket.objects.filter(
            modDescripcion__contains=patron_escalamiento
        ).order_by('-fecha_modificacion')
        
        ticket_ids = []
        for entrada in tickets_escalados:
            ticket_id = entrada.ticket.idTicket
            
            if ticket_id in tickets_asignados_ids:
                continue
            
            entrada_mas_reciente = HistoriaTicket.objects.filter(
                ticket__idTicket=ticket_id
            ).order_by('-fecha_modificacion', '-idCambioTicket').first()
            
            if entrada_mas_reciente and entrada_mas_reciente.idCambioTicket == entrada.idCambioTicket:
                ticket_ids.append(ticket_id)
        
        return Ticket.objects.filter(idTicket__in=ticket_ids)


def validar_ticket_asignado_a_empleado(ticket, empleado):
    """Valida si un ticket está asignado a un empleado específico"""
    return HistoriaTicket.objects.filter(
        ticket=ticket,
        empleado=empleado
    ).exists()


class EmpleadoLoginView(LoginView):
    template_name = 'logEmpleados.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Agregar clases CSS a los campos del formulario
        form.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingresa tu usuario'
        })
        form.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña'
        })
        return form
    
    def form_valid(self, form):
        # Verificar que el usuario sea un empleado activo
        user = form.get_user()
        
        # Verificar que no sea un cliente
        if hasattr(user, 'cliente'):
            messages.error(self.request, 'Los clientes deben usar el portal de clientes.')
            return self.form_invalid(form)
            
        # Verificar que no sea un administrador
        if hasattr(user, 'administrador'):
            messages.error(self.request, 'Los administradores deben usar el portal de administradores.')
            return self.form_invalid(form)
        
        try:
            empleado = user.empleado
            if not empleado.activo:
                messages.error(self.request, 'Tu cuenta está inactiva. Contacta al administrador.')
                return self.form_invalid(form)
        except Empleado.DoesNotExist:
            messages.error(self.request, 'No tienes permisos de empleado.')
            return self.form_invalid(form)
        
        messages.success(self.request, f'Bienvenido/a, {user.first_name}!')
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redirigir según el rol del empleado
        user = self.request.user
        if hasattr(user, 'empleado'):
            empleado = user.empleado
            if empleado.rol == 'supervisor':
                return reverse_lazy('empleados:supervisor_dashboard')
            else:
                return reverse_lazy('empleados:agente_dashboard')
        return reverse_lazy('empleados:dashboard')


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
        
        # Calcular tickets asignados por agente
        agentes_con_tickets = []
        for agente in agentes_mismo_nivel:
            tickets_asignados_ids = obtener_tickets_asignados_empleado(agente)
            agentes_con_tickets.append({
                'agente': agente,
                'tickets_count': len(tickets_asignados_ids)
            })
        
        # Obtener información de tickets asignados por nivel
        tickets_asignados_info = obtener_tickets_asignados_por_nivel(supervisor.nivel)
        tickets_asignados_ids = list(tickets_asignados_info.keys())
        
        # Obtener tickets sin asignar
        tickets_sin_asignar = obtener_tickets_sin_asignar_por_nivel(
            supervisor.nivel, 
            tickets_asignados_ids
        ).select_related('cliente')
        
        # Obtener tickets asignados con información completa
        tickets_asignados_query = Ticket.objects.filter(
            idTicket__in=tickets_asignados_ids
        ).select_related('cliente')
        
        tickets_asignados_info_list = []
        for ticket in tickets_asignados_query:
            ultima_historia = tickets_asignados_info.get(ticket.idTicket)
            if ultima_historia:
                tickets_asignados_info_list.append({
                    'ticket': ticket,
                    'agente_asignado': ultima_historia.empleado,
                    'estado': ultima_historia.estado,
                    'fecha_asignacion': ultima_historia.fecha_modificacion
                })

        context.update({
            'empleado': supervisor,
            'agentes': agentes_mismo_nivel,
            'agentes_con_tickets': agentes_con_tickets,
            'tickets_sin_asignar': tickets_sin_asignar,
            'tickets_asignados': tickets_asignados_info_list,
            'nivel_supervisor': supervisor.nivel
        })
        
        return context


@method_decorator(agente_required, name='dispatch')
class AgenteDashboardView(TemplateView):
    template_name = 'agente_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agente = self.request.user.empleado
        
        # Obtener tickets asignados a este agente
        tickets_asignados_ids = obtener_tickets_asignados_empleado(agente)
        tickets_asignados = Ticket.objects.filter(
            idTicket__in=tickets_asignados_ids
        ).select_related('cliente')
        
        # Procesar tickets con su estado actual
        tickets_con_estado = procesar_tickets_con_estado(tickets_asignados)
        
        # Separar tickets por estado
        tickets_pendientes = [t for t in tickets_con_estado if t['estado_actual'] and t['estado_actual'].nombreEstado == 'En Proceso']
        tickets_completados = [t for t in tickets_con_estado if t['estado_actual'] and t['estado_actual'].nombreEstado == 'Resuelto']
        
        context.update({
            'empleado': agente,
            'usuario': agente.user,
            'tickets_pendientes': tickets_pendientes,
            'tickets_completados': tickets_completados,
            'total_tickets': len(tickets_con_estado)
        })
        
        return context


@method_decorator(agente_required, name='dispatch')
class MisTicketsView(TemplateView):
    template_name = 'mis_tickets.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agente = self.request.user.empleado
        
        # Obtener tickets asignados a este agente
        tickets_asignados_ids = obtener_tickets_asignados_empleado(agente)
        tickets_asignados = Ticket.objects.filter(
            idTicket__in=tickets_asignados_ids
        ).select_related('cliente')
        
        # Procesar tickets con información completa para agente
        tickets_con_info = procesar_tickets_para_agente(tickets_asignados, agente)
        
        # Separar por estado
        tickets_pendientes = [t for t in tickets_con_info if t['estado_actual'] and t['estado_actual'].nombreEstado == 'En Proceso']
        tickets_resueltos = [t for t in tickets_con_info if t['estado_actual'] and t['estado_actual'].nombreEstado == 'Resuelto']
        
        context.update({
            'agente': agente,
            'tickets_pendientes': tickets_pendientes,
            'tickets_resueltos': tickets_resueltos,
            'total_tickets': len(tickets_con_info)
        })
        
        return context


@require_POST
@agente_required
def resolver_ticket(request):
    """Vista para que un agente resuelva un ticket"""
    try:
        ticket_id = request.POST.get('ticket_id')
        comentario = request.POST.get('comentario', '')
        
        if not ticket_id:
            return JsonResponse({'success': False, 'error': 'ID de ticket requerido'})
        
        # Obtener el ticket y el agente
        ticket = Ticket.objects.get(idTicket=ticket_id)
        agente = request.user.empleado
        
        # Verificar que el ticket está asignado a este agente
        if not validar_ticket_asignado_a_empleado(ticket, agente):
            return JsonResponse({'success': False, 'error': 'No tienes permisos para resolver este ticket'})
        
        # Obtener o crear el estado "Resuelto"
        estado_resuelto, created = Estado.objects.get_or_create(
            nombreEstado='Resuelto',
            defaults={'idEstado': 3}
        )
        
        # Crear entrada en HistoriaTicket para la resolución
        descripcion = f'Ticket resuelto por {agente.user.first_name} {agente.user.last_name}'
        if comentario:
            descripcion += f'. Comentario: {comentario}'
        
        HistoriaTicket.objects.create(
            modDescripcion=descripcion,
            fecha_modificacion=timezone.now().date(),
            empleado=agente,
            ticket=ticket,
            estado=estado_resuelto
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Ticket resuelto exitosamente'
        })
        
    except Ticket.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Ticket no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
@agente_required
def escalar_ticket(request):
    """Vista para que un agente escale un ticket al siguiente nivel"""
    try:
        ticket_id = request.POST.get('ticket_id')
        comentario = request.POST.get('comentario', '')
        
        if not ticket_id:
            return JsonResponse({'success': False, 'error': 'ID de ticket requerido'})
        
        # Obtener el ticket y el agente
        ticket = Ticket.objects.get(idTicket=ticket_id)
        agente = request.user.empleado
        
        # Verificar que el ticket está asignado a este agente
        if not validar_ticket_asignado_a_empleado(ticket, agente):
            return JsonResponse({'success': False, 'error': 'No tienes permisos para escalar este ticket'})
        
        # Verificar que se puede escalar (no está en el nivel máximo)
        if agente.nivel >= 3:  # Suponiendo máximo 3 niveles
            return JsonResponse({'success': False, 'error': 'No se puede escalar desde el nivel máximo'})
        
        # Obtener o crear el estado "En espera"
        estado_espera, created = Estado.objects.get_or_create(
            nombreEstado='En espera',
            defaults={'idEstado': 1}
        )
        
        # Crear entrada en HistoriaTicket para el escalamiento
        nivel_destino = agente.nivel + 1
        descripcion = f'Ticket escalado del nivel {agente.nivel} al nivel {nivel_destino} por {agente.user.get_full_name() or agente.user.username}'
        if comentario:
            descripcion += f'. Motivo: {comentario}'
        
        HistoriaTicket.objects.create(
            modDescripcion=descripcion,
            fecha_modificacion=timezone.now().date(),
            empleado=None,  # Al escalar, queda sin asignar para el siguiente nivel
            ticket=ticket,
            estado=estado_espera
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Ticket escalado al nivel {agente.nivel + 1} exitosamente'
        })
        
    except Ticket.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Ticket no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
@supervisor_required
def asignar_ticket(request):
    """Vista para asignar un ticket a un agente"""
    try:
        ticket_id = request.POST.get('ticket_id')
        agente_id = request.POST.get('agente_id')
        
        # Validar datos
        if not ticket_id or not agente_id:
            return JsonResponse({'success': False, 'error': 'Datos incompletos'})
        
        # Obtener el ticket y el agente
        ticket = Ticket.objects.get(idTicket=ticket_id)
        agente = Empleado.objects.get(id=agente_id, rol='agente')
        supervisor = request.user.empleado
        
        # Verificar que el agente es del mismo nivel que el supervisor
        if agente.nivel != supervisor.nivel:
            return JsonResponse({'success': False, 'error': 'No puedes asignar tickets a agentes de otro nivel'})
            
        # Verificar que el ticket pertenece al nivel del supervisor
        # Esto es una verificación adicional para garantizar que el supervisor solo asigne tickets de su nivel
        ultima_historia = HistoriaTicket.objects.filter(
            ticket=ticket
        ).order_by('-fecha_modificacion', '-idCambioTicket').first()
        
        # Para nivel 1: solo puede asignar tickets nuevos o de nivel 1
        # Para niveles superiores: solo puede asignar tickets escalados específicamente a su nivel
        if supervisor.nivel > 1:
            # Verificar si el ticket fue escalado a este nivel
            entradas_escalamiento = HistoriaTicket.objects.filter(
                ticket=ticket,
                modDescripcion__contains=f'al nivel {supervisor.nivel}'
            ).exists()
            
            if not entradas_escalamiento:
                return JsonResponse({'success': False, 'error': f'Este ticket no pertenece al nivel {supervisor.nivel}'})
        
        # Obtener o crear el estado "En Proceso"
        try:
            estado_en_proceso = Estado.objects.get(nombreEstado='En Proceso')
        except Estado.DoesNotExist:
            estado_en_proceso = Estado.objects.create(
                idEstado=2,
                nombreEstado='En Proceso'
            )
        
        # Crear entrada en HistoriaTicket para la asignación (directamente en proceso)
        HistoriaTicket.objects.create(
            modDescripcion=f'Ticket asignado a {agente.user.first_name or agente.user.username} {agente.user.last_name or ""} por {supervisor.user.first_name or supervisor.user.username} {supervisor.user.last_name or ""}',
            fecha_modificacion=timezone.now().date(),
            empleado=agente,
            ticket=ticket,
            estado=estado_en_proceso
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'Ticket asignado a {agente.user.get_full_name() or agente.user.username}'
        })
        
    except Ticket.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Ticket no encontrado'})
    except Empleado.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agente no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Vista personalizada de logout para empleados
class EmpleadoLogoutView(LogoutView):
    next_page = '/empleados/log/'  # Forzar redirección específica para empleados
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'Has cerrado sesión exitosamente.')
        # Forzar logout y redirección manual si es necesario
        logout(request)
        return redirect('/empleados/log/')

@login_required
@empleado_required
def obtener_detalles_ticket(request, ticket_id):
    """Vista para obtener los detalles completos de un ticket incluyendo su historial"""
    try:
        ticket = Ticket.objects.select_related('cliente__user').get(idTicket=ticket_id)
        
        # Obtener el historial del ticket
        historial = HistoriaTicket.objects.select_related(
            'estado', 'empleado__user'
        ).filter(ticket=ticket).order_by('fecha_modificacion')
        
        # Obtener el estado actual (último cambio)
        ultimo_estado = historial.last()
        estado_actual = ultimo_estado.estado.nombreEstado if ultimo_estado and ultimo_estado.estado else 'Sin estado'
        
        # Obtener el empleado asignado actual
        empleado_asignado = ultimo_estado.empleado if ultimo_estado and ultimo_estado.empleado else None
        
        # Preparar datos del ticket
        ticket_data = {
            'id': ticket.idTicket,
            'numero': f'TCK-{str(ticket.idTicket).zfill(4)}',
            'nombre': ticket.nombreTicket,
            'descripcion': ticket.descripcionTicket,
            'fecha_creacion': ticket.fechar_creacion.strftime('%Y-%m-%d %H:%M:%S'),
            'cliente': f"{ticket.cliente.user.first_name} {ticket.cliente.user.last_name}".strip() or ticket.cliente.user.username,
            'estado_actual': estado_actual,
            'empleado_asignado': f"{empleado_asignado.user.first_name} {empleado_asignado.user.last_name}".strip() or empleado_asignado.user.username if empleado_asignado else 'Sin asignar',
            'fecha_asignacion': ultimo_estado.fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S') if ultimo_estado else None,
        }
        
        # Preparar historial
        historial_data = []
        for cambio in historial:
            empleado_nombre = 'Sistema'
            if cambio.empleado:
                empleado_nombre = f"{cambio.empleado.user.first_name} {cambio.empleado.user.last_name}".strip() or cambio.empleado.user.username
            
            # Determinar el tipo de evento para el timeline
            tipo = 'info'
            if cambio.estado:
                if cambio.estado.nombreEstado == 'Resuelto':
                    tipo = 'success'
                elif cambio.estado.nombreEstado in ['En Proceso', 'Asignado']:
                    tipo = 'warning'
                elif cambio.estado.nombreEstado in ['Cerrado', 'Cancelado']:
                    tipo = 'danger'
            
            historial_data.append({
                'fecha': cambio.fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S'),
                'estado': cambio.estado.nombreEstado if cambio.estado else 'Cambio',
                'usuario': empleado_nombre,
                'tipo': tipo,
                'comentario': cambio.modDescripcion or 'Sin comentarios adicionales'
            })
        
        return JsonResponse({
            'success': True,
            'ticket': ticket_data,
            'historial': historial_data
        })
        
    except Ticket.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Ticket no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener detalles del ticket: {str(e)}'
        }, status=500)


@login_required
@supervisor_required
def obtener_detalles_empleado(request, empleado_id):
    """Vista para obtener los detalles completos de un empleado incluyendo sus estadísticas"""
    try:
        empleado = Empleado.objects.select_related('user').get(id=empleado_id)
        supervisor = request.user.empleado
        
        # Verificar que el empleado pertenece al mismo nivel que el supervisor
        if empleado.nivel != supervisor.nivel:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para ver este empleado'
            }, status=403)
        
        # Obtener tickets asignados usando helper function
        tickets_asignados_ids = obtener_tickets_asignados_empleado(empleado)
        total_tickets = len(tickets_asignados_ids)
        
        # Inicializar estadísticas
        tickets_resueltos = 0
        tickets_pendientes = 0
        tickets_recientes = []
        
        if total_tickets > 0:
            # Obtener tickets y procesar con helper function
            tickets_asignados = Ticket.objects.filter(
                idTicket__in=tickets_asignados_ids
            ).select_related('cliente__user')
            
            tickets_con_estado = procesar_tickets_con_estado(tickets_asignados)
            
            # Contar por estado
            for ticket_info in tickets_con_estado:
                if ticket_info['estado_actual']:
                    if ticket_info['estado_actual'].nombreEstado == 'Resuelto':
                        tickets_resueltos += 1
                    elif ticket_info['estado_actual'].nombreEstado == 'En Proceso':
                        tickets_pendientes += 1
            
            # Obtener los últimos 5 tickets del empleado
            ultimos_tickets = tickets_asignados.order_by('-fechar_creacion')[:5]
            for ticket in ultimos_tickets:
                ultimo_estado = obtener_ultimo_estado_ticket(ticket)
                
                tickets_recientes.append({
                    'id': ticket.idTicket,
                    'numero': f'TCK-{str(ticket.idTicket).zfill(4)}',
                    'cliente': f"{ticket.cliente.user.first_name} {ticket.cliente.user.last_name}".strip() or ticket.cliente.user.username,
                    'estado': ultimo_estado.estado.nombreEstado if ultimo_estado and ultimo_estado.estado else 'Sin estado',
                    'fecha': ticket.fechar_creacion.strftime('%d/%m/%Y')
                })
        
        # Preparar datos del empleado
        empleado_data = {
            'id': empleado.id,
            'nombre_completo': f"{empleado.user.first_name} {empleado.user.last_name}".strip() or empleado.user.username,
            'username': empleado.user.username,
            'email': empleado.user.email,
            'telefono': str(empleado.telefono) if empleado.telefono else 'No disponible',
            'activo': empleado.activo,
            'rol': empleado.get_rol_display(),
            'nivel': empleado.nivel,
            'fecha_ingreso': empleado.user.date_joined.strftime('%d/%m/%Y'),
            'estadisticas': {
                'tickets_asignados': total_tickets,
                'tickets_resueltos': tickets_resueltos,
                'tickets_pendientes': tickets_pendientes
            },
            'tickets_recientes': tickets_recientes
        }
        
        return JsonResponse({
            'success': True,
            'empleado': empleado_data
        })
        
    except Empleado.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Empleado no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener detalles del empleado: {str(e)}'
        }, status=500)
