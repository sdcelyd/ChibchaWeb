from django.db import models
from Clientes.models import Cliente
from .validators import validar_tarjeta

class TarjetaCredito(models.Model):
    numero = models.CharField(max_length=16, validators=[validar_tarjeta])
    nombre_titular = models.CharField(max_length=50)
    fecha_expiracion = models.CharField(max_length=5)
    cvv = models.CharField(max_length=4)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='tarjetas')

    def __str__(self):
        return f"**** **** **** {self.numero[-4:]}"