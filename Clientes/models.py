from django.db import models

class Cliente (models.Model):
    #Modelo de la tabla Clientes para la base de datos
    clienteId=models.AutoField(primary_key=True,unique=True)
    nickname=models.CharField(max_length=15)
    email=models.CharField(max_length=20)
    nombre=models.CharField(max_length=15, verbose_name='nombre')
    contrasena=models.CharField(max_length=15, verbose_name='contraseña')
    telefono=models.CharField(max_length=15,blank=True)
    metodoPago=models.BooleanField(default=False, verbose_name='método de pago')

    def __str__(self):
        return self.nickname