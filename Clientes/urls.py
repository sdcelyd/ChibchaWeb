from django.urls import path
from .views import registrar_cliente, borrar_cliente, editar_cliente
from django.shortcuts import render

urlpatterns = [
    path('registrar/', registrar_cliente, name='registrar_cliente'),
    path('exito/', lambda request: render(request, 'clientes/exito.html'), name='registro_exitoso'),
    path('Clientes/<int:cliente_id>/borrar/', borrar_cliente, name='borrar_cliente'),
    path('editar/<int:cliente_id>/', editar_cliente, name='editar_cliente'),
]