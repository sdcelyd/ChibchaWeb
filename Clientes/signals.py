from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Cliente
from Distribuidor.models import Distribuidor  # Importa desde la otra app

@receiver(post_save, sender=Cliente)
def crear_distribuidor_si_corresponde(sender, instance, created, **kwargs):
    if instance.es_distribuidor:
        # Solo si no existe aún el perfil
        if not hasattr(instance, 'perfil_distribuidor'):
            Distribuidor.objects.create(cliente=instance)

            # (Opcional) hacerlo staff
            if not instance.user.is_staff:
                instance.user.is_staff = True
                instance.user.save()