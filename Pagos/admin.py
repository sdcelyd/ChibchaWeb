from django.contrib import admin
from .models import TarjetaCredito, Direccion, Pais, Pago


admin.site.register(Direccion)
admin.site.register(TarjetaCredito)
admin.site.register(Pais)
admin.site.register(Pago)