from django.contrib import admin
from .models import Administrador

@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('user', 'activo', 'fecha_registro', 'ultimo_acceso')
    list_filter = ('activo', 'fecha_registro', 'puede_gestionar_usuarios', 'puede_ver_estadisticas')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('fecha_registro', 'ultimo_acceso')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'activo')
        }),
        ('Permisos', {
            'fields': ('puede_gestionar_usuarios', 'puede_ver_estadisticas', 'puede_gestionar_pagos')
        }),
        ('Fechas', {
            'fields': ('fecha_registro', 'ultimo_acceso'),
            'classes': ('collapse',)
        })
    )
