from django.urls import path
from . import views

app_name = 'empleados'

urlpatterns = [
    path('login/', views.EmpleadoLoginView.as_view(), name='login'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/supervisor/', views.SupervisorDashboardView.as_view(), name='supervisor_dashboard'),
    path('dashboard/agente/', views.AgenteDashboardView.as_view(), name='agente_dashboard'),
    path('logout/', views.EmpleadoLogoutView.as_view(), name='logout'),
]
