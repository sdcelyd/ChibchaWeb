from django.contrib import admin
from .models import TarjetaCredito, Direccion, Pais, Pago, PagoDistribuidor


admin.site.register(Direccion)
admin.site.register(TarjetaCredito)
admin.site.register(Pais)
admin.site.register(Pago)
admin.site.register(PagoDistribuidor)