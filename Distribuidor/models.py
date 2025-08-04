from django.db import models
from Clientes.models import Cliente


class Distribuidor(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='perfil_distribuidor')

    TIPO_DISTRIBUIDOR_CHOICES = [
        ('BASICO', 'Básico'),
        ('PREMIUM', 'Premium'),
    ]

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_DISTRIBUIDOR_CHOICES,
        default='BASICO'
    )

    cantidad_dominios = models.PositiveIntegerField(default=0)

    @property
    def comision(self):
        return 0.15 if self.tipo == 'PREMIUM' else 0.10

    def __str__(self):
        return f"{self.cliente.user.username} - {self.tipo}"
