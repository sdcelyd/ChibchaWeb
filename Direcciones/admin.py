from django.contrib import admin

# Register your models here.
from .models import Direccion, Pais

admin.site.register(Direccion)
admin.site.register(Pais)
