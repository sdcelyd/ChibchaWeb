from django.urls import path
from .views import dashboard_distribuidor, mis_paquetes

app_name = 'distribuidores'

urlpatterns = [
    path('dashboard/', dashboard_distribuidor, name='dashboard'),
    path('mis-paquetes/', mis_paquetes, name='mis_paquetes'),
]
