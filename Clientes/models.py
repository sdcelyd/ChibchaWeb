from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ChibchaWeb.planes import PLANES_DISPONIBLES

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    telefono = models.IntegerField(blank=True)
    es_distribuidor = models.BooleanField(default=False)

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
    
    @property
    def limite_dominios(self):
        """Retorna el límite de dominios según el plan del cliente"""
        if not self.plan:
            return 1  # Plan por defecto
        
        # Buscar el plan en los planes disponibles
        for nombre_plan, detalles in PLANES_DISPONIBLES.items():
            if nombre_plan.lower() == self.plan.lower():
                return detalles.get('webs', 1)
        
        # Si no encuentra el plan, retornar 1 por defecto
        return 1
    
    @property
    def dominios_count(self):
        """Retorna la cantidad actual de dominios del PLAN de hosting (no incluye dominios de distribuidor)"""
        from Dominios.models import Dominios
        return Dominios.objects.filter(clienteId=self, compraDistribuidor=False).count()
    
    @property
    def total_dominios_count(self):
        """Retorna la cantidad total de dominios (plan + distribuidor)"""
        from Dominios.models import Dominios
        return Dominios.objects.filter(clienteId=self).count()
    
    @property
    def dominios_distribuidor_count(self):
        """Retorna la cantidad de dominios creados por distribuidor"""
        from Dominios.models import Dominios
        return Dominios.objects.filter(clienteId=self, compraDistribuidor=True).count()
    
    @property
    def puede_agregar_dominios(self):
        """Verifica si puede agregar más dominios según su plan (solo cuenta dominios del plan de hosting)"""
        return self.dominios_count < self.limite_dominios