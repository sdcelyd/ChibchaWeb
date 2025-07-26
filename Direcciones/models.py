from django.db import models
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
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='direcciones')

    def __str__(self):
        return f"{self.ubicacion}, {self.codigoPostal}, {self.pais}"