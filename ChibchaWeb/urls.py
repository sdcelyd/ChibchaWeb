from django.contrib import admin
from django.urls import include, path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  
    path('Clientes/', include('Clientes.urls')),
    path('pagos/', include('Pagos.urls')),
    path('empleados/', include('Empleados.urls')),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/<int:cliente_id>/', views.detalle_cliente, name='detalle_cliente'), 
    path('login/', views.ClienteLoginView.as_view(), name='login'),
    path('exitologin/', views.vista_exito, name='exitologin'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin-panel/', include('Administradores.urls')),
]
