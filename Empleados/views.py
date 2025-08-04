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
        return '/empleados/dashboard/'


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
        
        tickets_asignados_info = {}
        
        # Obtenemos la última entrada del historial para cada ticket que tenga un empleado asignado
        ultimas_historias = HistoriaTicket.objects.filter(
            empleado__isnull=False
        ).values('ticket__idTicket').annotate(
            ultima_fecha=Max('fecha_modificacion')
        )
        
        # Para cada ticket con una última entrada, verificamos si el empleado asignado es de este nivel
        for historia in ultimas_historias:
            ticket_id = historia['ticket__idTicket']
            ultima_fecha = historia['ultima_fecha']
            
            # Buscamos la entrada más reciente con esa fecha para ese ticket
            ultima_entrada = HistoriaTicket.objects.filter(
                ticket__idTicket=ticket_id,
                fecha_modificacion=ultima_fecha
            ).order_by('-idCambioTicket').first()
            
            if ultima_entrada and ultima_entrada.empleado and ultima_entrada.empleado.nivel == supervisor.nivel:
                tickets_asignados_info[ticket_id] = ultima_entrada
        
        # Convertimos a lista de IDs para usar en consultas
        tickets_asignados_ids = list(tickets_asignados_info.keys())
        
        if supervisor.nivel == 1:
            # Para nivel 1: tickets nuevos sin asignar a ningún empleado
            tickets_sin_asignar_query = Ticket.objects.filter(
                ~Q(idTicket__in=tickets_asignados_ids)  # Excluir los ya asignados
            ).filter(
                # Solo incluir tickets que no tengan ninguna asignación o solo tengan entradas sin empleado
                ~Q(idTicket__in=HistoriaTicket.objects.filter(
                    empleado__isnull=False
                ).exclude(
                    empleado__nivel=supervisor.nivel
                ).values_list('ticket__idTicket', flat=True))
            )
        else:
            # Para niveles superiores: tickets escalados a este nivel específico y que no estén asignados
            # Obtenemos los tickets que tienen una entrada de escalamiento al nivel actual
            ultimas_entradas = {}
            
            # Modificamos la búsqueda para ser más flexible con el formato del mensaje de escalamiento
            # Buscamos específicamente tickets escalados AL nivel del supervisor (no DESDE ese nivel)
            patron_escalamiento = f'al nivel {supervisor.nivel}'  # Cambiado para ser más específico
            
            # Primera estrategia: buscar entradas que contengan el patrón específico
            todas_entradas = HistoriaTicket.objects.filter(
                modDescripcion__contains=patron_escalamiento
            ).order_by('-fecha_modificacion')
            
            # Segunda estrategia: si no hay resultados, buscar por expresión regular más general
            if todas_entradas.count() == 0:
                print(f"No se encontraron tickets con el patrón exacto. Probando búsqueda alternativa...")
                todas_entradas = HistoriaTicket.objects.filter(
                    Q(modDescripcion__contains=f'escalado') & 
                    Q(modDescripcion__contains=f'al nivel {supervisor.nivel}')
                ).order_by('-fecha_modificacion')
            
            # Imprimimos para depuración (en desarrollo)
            print(f"Búsqueda para supervisor nivel {supervisor.nivel}")
            print(f"Patrón de búsqueda principal: '{patron_escalamiento}'")
            print(f"Tickets encontrados: {todas_entradas.count()}")
            
            # Para cada ticket, imprimimos detalles para depuración
            for entrada in todas_entradas:
                print(f"Ticket ID: {entrada.ticket.idTicket}, Descripción: {entrada.modDescripcion}")
                print(f"Fecha modificación: {entrada.fecha_modificacion}, Empleado: {entrada.empleado}")
                print(f"Estado: {entrada.estado.nombreEstado if entrada.estado else 'Sin estado'}")
            
            # Para cada ticket, nos quedamos con la entrada más reciente
            ticket_ids = []
            for entrada in todas_entradas:
                ticket_id = entrada.ticket.idTicket
                
                # Verificamos si el ticket está en la lista de asignados basada en la última entrada del historial
                if ticket_id in tickets_asignados_ids:
                    # Si está asignado, imprimimos para depuración
                    print(f"Ticket {ticket_id} ya está asignado a un agente de nivel {supervisor.nivel}")
                    continue
                
                # Si aún no hemos procesado este ticket
                if ticket_id not in ultimas_entradas:
                    ultimas_entradas[ticket_id] = entrada
                    
                    # Verificamos que esta entrada de escalamiento sea la última acción en el ticket
                    # Es decir, no debe haber entradas más recientes que esta
                    entradas_posteriores = HistoriaTicket.objects.filter(
                        ticket__idTicket=ticket_id,
                        fecha_modificacion__gt=entrada.fecha_modificacion
                    )
                    
                    if entradas_posteriores.exists():
                        print(f"Ticket {ticket_id} tiene entradas posteriores al escalamiento")
                        continue
                    
                    # Si llegamos aquí, el ticket está escalado y no asignado
                    ticket_ids.append(ticket_id)
                    print(f"Agregando ticket {ticket_id} - {entrada.modDescripcion}")
            
            # Finalizamos la consulta para obtener los tickets
            tickets_sin_asignar_query = Ticket.objects.filter(idTicket__in=ticket_ids)
            
            # Log para depuración
            print(f"IDs de tickets a mostrar: {ticket_ids}")
            print(f"Cantidad de tickets a mostrar: {len(ticket_ids)}")
            
        tickets_sin_asignar = tickets_sin_asignar_query.select_related('cliente')
        
        # Verificación final
        print(f"Tickets sin asignar (QuerySet): {tickets_sin_asignar.count()}")
        for t in tickets_sin_asignar:
            print(f"Ticket en QuerySet final: ID={t.idTicket}, Nombre={t.nombreTicket}")
        
        # Obtener tickets asignados a agentes de este nivel con información completa
        # Utilizamos los IDs que ya calculamos antes
        tickets_asignados_query = Ticket.objects.filter(
            idTicket__in=tickets_asignados_ids
        ).select_related('cliente')
        
        # Crear lista con información de asignación y estado
        tickets_asignados_info_list = []
        for ticket in tickets_asignados_query:
            # Usamos la entrada que ya encontramos anteriormente
            ultima_historia = tickets_asignados_info.get(ticket.idTicket)
            
            if ultima_historia:
                tickets_asignados_info_list.append({
                    'ticket': ticket,
                    'agente_asignado': ultima_historia.empleado,
                    'estado': ultima_historia.estado,
                    'fecha_asignacion': ultima_historia.fecha_modificacion
                })

        context['empleado'] = supervisor
        context['agentes'] = agentes_mismo_nivel
        context['tickets_sin_asignar'] = tickets_sin_asignar
        context['tickets_asignados'] = tickets_asignados_info_list
        context['nivel_supervisor'] = supervisor.nivel
        
        return context


@method_decorator(agente_required, name='dispatch')
class AgenteDashboardView(TemplateView):
    template_name = 'agente_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agente = self.request.user.empleado
        
        # Obtener tickets asignados a este agente
        tickets_asignados_ids = HistoriaTicket.objects.filter(
            empleado=agente
        ).values_list('ticket__idTicket', flat=True).distinct()
        
        tickets_asignados = Ticket.objects.filter(
            idTicket__in=tickets_asignados_ids
        ).select_related('cliente')
        
        # Obtener el estado actual de cada ticket
        tickets_con_estado = []
        for ticket in tickets_asignados:
            ultimo_estado = HistoriaTicket.objects.filter(
                ticket=ticket
            ).order_by('-fecha_modificacion', '-idCambioTicket').first()
            
            tickets_con_estado.append({
                'ticket': ticket,
                'estado': ultimo_estado.estado if ultimo_estado else None,
                'fecha_modificacion': ultimo_estado.fecha_modificacion if ultimo_estado else None
            })
        
        # Separar tickets por estado (solo "En Proceso" como pendientes)
        tickets_pendientes = [t for t in tickets_con_estado if t['estado'] and t['estado'].nombreEstado == 'En Proceso']
        tickets_completados = [t for t in tickets_con_estado if t['estado'] and t['estado'].nombreEstado == 'Resuelto']
        
        context['empleado'] = agente
        context['usuario'] = agente.user
        context['tickets_pendientes'] = tickets_pendientes
        context['tickets_completados'] = tickets_completados
        context['total_tickets'] = len(tickets_con_estado)
        
        return context


@method_decorator(agente_required, name='dispatch')
class MisTicketsView(TemplateView):
    template_name = 'mis_tickets.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agente = self.request.user.empleado
        
            # Obtener todos los tickets asignados a este agente
        tickets_asignados_ids = HistoriaTicket.objects.filter(
            empleado=agente
        ).values_list('ticket__idTicket', flat=True).distinct()
        
        tickets_asignados = Ticket.objects.filter(
            idTicket__in=tickets_asignados_ids
        ).select_related('cliente')
        
        # Obtener el estado actual de cada ticket con toda la información del historial
        tickets_con_info = []
        for ticket in tickets_asignados:
            ultimo_estado = HistoriaTicket.objects.filter(
                ticket=ticket
            ).order_by('-fecha_modificacion', '-idCambioTicket').first()
            
            # Obtener el historial completo del ticket
            historial = HistoriaTicket.objects.filter(
                ticket=ticket
            ).order_by('-fecha_modificacion').select_related('empleado__user', 'estado')
            
            tickets_con_info.append({
                'ticket': ticket,
                'estado_actual': ultimo_estado.estado if ultimo_estado else None,
                'fecha_ultima_modificacion': ultimo_estado.fecha_modificacion if ultimo_estado else None,
                'historial': historial,
                'puede_resolver': ultimo_estado and ultimo_estado.estado.nombreEstado == 'En Proceso',
                'puede_escalar': ultimo_estado and ultimo_estado.estado.nombreEstado == 'En Proceso' and agente.nivel < 3  # Suponiendo máximo 3 niveles
            })
        
        # Separar por estado (sin "Cerrado", solo "Resuelto")
        tickets_pendientes = [t for t in tickets_con_info if t['estado_actual'] and t['estado_actual'].nombreEstado == 'En Proceso']
        tickets_resueltos = [t for t in tickets_con_info if t['estado_actual'] and t['estado_actual'].nombreEstado == 'Resuelto']
        
        context['agente'] = agente
        context['tickets_pendientes'] = tickets_pendientes
        context['tickets_resueltos'] = tickets_resueltos
        context['total_tickets'] = len(tickets_con_info)
        
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
        
        # Obtener el ticket y verificar que está asignado al agente
        ticket = Ticket.objects.get(idTicket=ticket_id)
        agente = request.user.empleado
        
        # Verificar que el ticket está asignado a este agente
        ticket_asignado = HistoriaTicket.objects.filter(
            ticket=ticket,
            empleado=agente
        ).exists()
        
        if not ticket_asignado:
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
        ticket_asignado = HistoriaTicket.objects.filter(
            ticket=ticket,
            empleado=agente
        ).exists()
        
        if not ticket_asignado:
            return JsonResponse({'success': False, 'error': 'No tienes permisos para escalar este ticket'})
        
        # Verificar que se puede escalar (no está en el nivel máximo)
        if agente.nivel >= 3:  # Suponiendo máximo 3 niveles
            return JsonResponse({'success': False, 'error': 'No se puede escalar desde el nivel máximo'})
        
        # Obtener o crear el estado "En espera" para el escalamiento (el supervisor del siguiente nivel lo asignará)
        estado_espera, created = Estado.objects.get_or_create(
            nombreEstado='En espera',
            defaults={'idEstado': 1}
        )
        
        # Crear entrada en HistoriaTicket para el escalamiento
        nivel_destino = agente.nivel + 1
        
        # Formato estandarizado con "al nivel X" para que solo lo vea el supervisor correcto
        # IMPORTANTE: Usamos "al nivel X" para que coincida exactamente con la búsqueda del supervisor
        descripcion = f'Ticket escalado del nivel {agente.nivel} al nivel {nivel_destino} por {agente.user.get_full_name() or agente.user.username}'
        if comentario:
            descripcion += f'. Motivo: {comentario}'
        
        # Registrar el escalamiento en el historial
        escalamiento = HistoriaTicket.objects.create(
            modDescripcion=descripcion,
            fecha_modificacion=timezone.now().date(),
            empleado=None,  # Al escalar, queda sin asignar para el siguiente nivel
            ticket=ticket,
            estado=estado_espera
        )
        
        # Para propósitos de depuración
        print(f"Ticket {ticket.idTicket} escalado al nivel {nivel_destino}")
        print(f"Descripción: {descripcion}")
        print(f"ID de historia: {escalamiento.idCambioTicket}")
        
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
