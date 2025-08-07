from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('registrar-direccion/', views.registrar_direccion, name='registrar_direccion'),
    path('registrar-tarjeta/', views.registrar_tarjeta, name='registrar_tarjeta'),
    path('eliminar-direccion/<int:direccion_id>/', views.eliminar_direccion, name='eliminar_direccion'),
    path('eliminar-tarjeta/<int:tarjeta_id>/', views.eliminar_tarjeta, name='eliminar_tarjeta'),
    path("seleccionar-plan/", views.seleccionar_plan, name="seleccionar_plan"),
    path("seleccionar-direccion-tarjeta/", views.seleccionar_direccion_tarjeta, name="seleccionar_direccion_tarjeta"),
    path("resumen-pago/", views.resumen_pago, name="resumen_pago"),
    path("confirmacion-pago/", views.confirmacion_pago, name="confirmacion_pago"),
    path("seleccionar-paquete/", views.seleccionar_paquete, name="seleccionar_paquete"),
    path("resumen-pago-paquetes/", views.resumen_pago_paquetes, name="resumen_pago_paquetes"),
    path('confirmacion-pago-paquetes/', views.confirmacion_pago_paquetes, name='confirmacion_pago_paquetes'),
]
