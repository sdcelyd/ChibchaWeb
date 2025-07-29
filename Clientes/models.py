from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    # Relación uno a uno con el modelo de usuario estándar de Django
    # Este campo conecta con los datos de autenticación (username, email, password, etc.)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Teléfono adicional que no está en el modelo User
    telefono = models.CharField(max_length=15, blank=True)

    # Indica si el cliente ya tiene un método de pago registrado (TarjetaCredito, etc.)
    metodoPago = models.BooleanField(default=False, verbose_name='método de pago')

    def __str__(self):
        # Muestra el username del usuario en representaciones del modelo
        return self.user.username