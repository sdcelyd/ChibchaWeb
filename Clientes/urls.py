from django.urls import path
from .views import registrar_cliente, borrar_cliente, editar_cliente, detalle_cliente, perfil, mis_hosts
from django.shortcuts import render
from . import views

app_name = 'clientes' #Namespace para la app
    
urlpatterns = [
    path('registrar/', registrar_cliente, name='registrar_cliente'),
    path('exito/', lambda request: render(request, 'exito.html'), name='registro_exitoso'),
    path('detalle/', detalle_cliente, name='detalle_cliente'),
    path('editar/<int:cliente_id>/', editar_cliente, name='editar_cliente'),
    path('borrar/', borrar_cliente, name='borrar_cliente'),
    path('mis-hosts/', mis_hosts, name='mis_hosts'),
    path('perfil/', perfil, name='perfil'),
    path('home/', views.home_cliente, name='home_clientes'),
    path('quiero-ser-distribuidor/', views.quiero_ser_distribuidor, name='quiero_ser_distribuidor'),
    path('confirmar-ser-distribuidor/', views.hacer_distribuidor, name='hacer_distribuidor'),
    path('distribuidor-exito/', views.distribuidor_exito, name='distribuidor_exito'),
]