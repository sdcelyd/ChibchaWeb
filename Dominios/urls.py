from django.urls import path
from . import views

urlpatterns = [
    path('', views.verificar_url, name='verificar_url'),
    path('generar-xml/', views.generar_xml, name='generar_xml'),
]