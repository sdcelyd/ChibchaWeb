from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('registrar-direccion/', views.registrar_direccion, name='registrar_direccion'),
    path('registrar-tarjeta/', views.registrar_tarjeta, name='registrar_tarjeta'),
    path('eliminar-direccion/<int:direccion_id>/', views.eliminar_direccion, name='eliminar_direccion'),
    path('eliminar-tarjeta/<int:tarjeta_id>/', views.eliminar_tarjeta, name='eliminar_tarjeta'),
]
