from django.urls import path
from . import views


app_name = 'empleados'  # Namespace for the app

urlpatterns = [
    path('log/', views.EmpleadoLoginView.as_view(), name='log'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    #path('dashboard/supervisor/', views.SupervisorDashboardView.as_view(), name='supervisor_dashboard'),
    path('dashboard/supervisor/', views.DashboardSupervisorView.as_view(), name='supervisor_dashboard'),
    path('dashboard/agente/', views.AgenteDashboardView.as_view(), name='agente_dashboard'),
    path('logout/', views.EmpleadoLogoutView.as_view(), name='logout'),
]
