from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'administradores'

urlpatterns = [
    # Autenticación
    path('login/', views.AdministradorLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='administradores:login'), name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Gestión de usuarios
    path('usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    
    # Estadísticas
    path('estadisticas/pagos/', views.estadisticas_pagos, name='estadisticas_pagos'),
    path('estadisticas/usuarios/', views.estadisticas_usuarios, name='estadisticas_usuarios'),
    
    # API para gráficos
    path('api/graficos/', views.api_datos_grafico, name='api_datos_grafico'),
]