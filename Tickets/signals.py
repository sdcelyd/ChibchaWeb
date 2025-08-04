from django.db.models.signals import post_save
from django.dispatch import receiver
from Empleados.models import Empleado
from .models import Ticket, Estado, HistoriaTicket

@receiver(post_save, sender=Ticket)
def crear_historia_inicial(sender, instance, created, **kwargs):
    if created:
        supervisor_nivel_1 = Empleado.objects.filter(rol="supervisor", nivel=1).first()
        if supervisor_nivel_1:
            estado_espera, _ = Estado.objects.get_or_create(
                nombreEstado="En espera",
                defaults={"idEstado": 1}
            )
            HistoriaTicket.objects.create(
                ticket=instance,
                estado=estado_espera,
                empleado=supervisor_nivel_1,
                modDescripcion="Creación del ticket"
            )
