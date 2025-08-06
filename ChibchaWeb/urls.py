from django.contrib import admin
from django.urls import include, path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

import Dominios

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
    path('tickets/', include('Tickets.urls', namespace='tickets')),
    path('distribuidor/', include('Distribuidor.urls', namespace='distribuidores')),
    path('verificar-url/', include('Dominios.urls')),
    path('verificar-url/', Dominios.views.verificar_url, name='verificar-url'),
    path('administradores/', include('Administradores.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]
