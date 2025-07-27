from django.urls import path
from .views import registrar_cliente, cliente_login
from django.shortcuts import render

app_name = 'clientes' #Namespace para la app
    
urlpatterns = [
    path('login/', cliente_login, name='login'),
    path('registrar/', registrar_cliente, name='registrar_cliente'),
    path('exito/', lambda request: render(request, 'clientes/exito.html'), name='registro_exitoso'),
]