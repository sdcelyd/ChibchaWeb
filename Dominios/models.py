from django.db import models
from Clientes.models import Cliente

class Dominios(models.Model):
    clienteId = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='clienteId')
    nombreDominio = models.CharField(max_length=255, unique=True)
    compraDistribuidor = models.BooleanField(default=False, help_text="Indica si el dominio fue comprado por un distribuidor")

    class Meta:
        db_table = 'Dominios'

    def __str__(self):
        return f"{self.nombreDominio} - Cliente: {self.clienteId.user.username} - Distribuidor: {self.compraDistribuidor}"
