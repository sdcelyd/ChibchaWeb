from django.urls import path
from . import views

app_name = 'dominios'

urlpatterns = [
    path('', views.verificar_url, name='verificar_url'),
    path('agregar-dominio/', views.agregar_dominio, name='agregar_dominio'),
    path('eliminar-dominio/<int:dominio_id>/', views.eliminar_dominio, name='eliminar_dominio'),
]