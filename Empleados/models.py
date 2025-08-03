from django.db import models
from django.contrib.auth.models import User

# Creacion empleado encargado de la gestion de tickets
class Empleado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.IntegerField(blank=True)
    activo = models.BooleanField(default=True, verbose_name='activo')
    rol = models.CharField(max_length=50, choices=[
        ('supervisor', 'Supervisor'),
        ('agente', 'Agente'),
    ])
    nivel = models.IntegerField(default=1, choices=[
        (1, 'Nivel 1'),
        (2, 'Nivel 2'),
        (3, 'Nivel 3'),
    ], verbose_name='nivel de acceso')
    
    def __str__(self):
        return f"Empleado: {self.user.username}, Rol: {self.rol}, Nivel: {self.nivel}"