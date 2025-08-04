from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ticket, Estado, HistoriaTicket

@receiver(post_save, sender=Ticket)
def crear_historia_inicial(sender, instance, created, **kwargs):
    if created:
        estado_espera, _ = Estado.objects.get_or_create(
            nombreEstado="En espera",
            defaults={"idEstado": 1}
        )
        HistoriaTicket.objects.create(
            ticket=instance,
            estado=estado_espera,
            modDescripcion="Creación del ticket"
        )
