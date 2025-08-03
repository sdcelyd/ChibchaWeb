from django.db import models
from django.contrib.auth.models import User


class Administrador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    
    # Permisos específicos del administrador
    puede_gestionar_usuarios = models.BooleanField(default=True)
    puede_ver_estadisticas = models.BooleanField(default=True)
    puede_gestionar_pagos = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Admin: {self.user.username}"
    
    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"