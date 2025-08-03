from django.urls import path
from .views import registrar_cliente, borrar_cliente, editar_cliente
from .views import detalle_cliente
from django.shortcuts import render
from . import views


app_name = 'clientes' #Namespace para la app
    
urlpatterns = [
    path('registrar/', registrar_cliente, name='registrar_cliente'),
    path('exito/', lambda request: render(request, 'clientes/exito.html'), name='registro_exitoso'),
    path('<int:cliente_id>/', detalle_cliente, name='detalle_cliente'),
    path('editar/<int:cliente_id>/', editar_cliente, name='editar_cliente'),
    path('borrar/', views.borrar_cliente, name='borrar_cliente'),
    path('detalle/', views.detalle_cliente, name='detalle_cliente'),
]