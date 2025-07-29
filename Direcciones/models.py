from django.db import models
from .validators import VALIDADORES_DIRECCIONES
from Clientes.models import Cliente  

class Pais(models.Model):
    paisId = models.AutoField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Paises"
        verbose_name = "Pais"

class Direccion(models.Model):
    direccionId = models.AutoField(primary_key=True, unique=True)
    ubicacion = models.CharField(max_length=50)
    codigoPostal = models.CharField(max_length=10)
    
    # Relación con el país de esta dirección
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    
    # Relación con el cliente (que a su vez está vinculado al User)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='direcciones')

    def clean(self):
        """Valida la ubicación usando una función por país (si existe)."""
        super().clean()
        validador = VALIDADORES_DIRECCIONES.get(self.pais.nombre.lower())
        if validador:
            validador(self.ubicacion)

    def __str__(self):
        return f"{self.ubicacion}, {self.codigoPostal}, {self.pais}"