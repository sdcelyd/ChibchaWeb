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

    cantidad_dominios = models.PositiveIntegerField(default=0, help_text="Total de páginas compradas")
    paginas_vendidas = models.PositiveIntegerField(default=0, help_text="Cantidad de páginas ya vendidas")

    @property
    def comision(self):
        return 0.15 if self.tipo == 'PREMIUM' else 0.10

    @property
    def paginas_disponibles(self):
        """Páginas disponibles para vender (total - vendidas)"""
        return self.cantidad_dominios - self.paginas_vendidas

    def __str__(self):
        return f"{self.cliente.user.username} - {self.tipo}"
