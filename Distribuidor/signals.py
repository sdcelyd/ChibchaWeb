from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Distribuidor

@receiver(pre_save, sender=Distribuidor)
def actualizar_tipo_distribuidor(sender, instance, **kwargs):
    if instance.cantidad_dominios > 100:
        instance.tipo = 'PREMIUM'
    else:
        instance.tipo = 'BASICO'