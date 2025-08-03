from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    telefono = models.IntegerField(blank=True)

    # Campos de suscripción
    tiene_suscripcion = models.BooleanField(default=False)
    plan = models.CharField(max_length=50, blank=True, null=True)
    fecha_inicio_suscripcion = models.DateTimeField(blank=True, null=True)
    fecha_fin_suscripcion = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    @property
    def suscripcion_activa(self):
        return self.tiene_suscripcion and (not self.fecha_fin_suscripcion or self.fecha_fin_suscripcion > timezone.now())