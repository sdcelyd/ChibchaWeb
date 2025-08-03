from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Administradores.models import Administrador

class Command(BaseCommand):
    help = 'Crear un superadministrador para el sistema'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username del administrador')
        parser.add_argument('--email', type=str, help='Email del administrador')
        parser.add_argument('--password', type=str, help='Password del administrador')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email'] 
        password = options['password']
        
        # Validar que se proporcionen todos los argumentos
        if not all([username, email, password]):
            self.stdout.write(
                self.style.ERROR('Debes proporcionar --username, --email y --password')
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'El usuario {username} ya existe')
            )
            return

        try:
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True,
                is_superuser=True
            )

            # Crear perfil de administrador
            administrador = Administrador.objects.create(
                user=user,
                activo=True,
                puede_gestionar_usuarios=True,
                puede_ver_estadisticas=True,
                puede_gestionar_pagos=True
            )

            self.stdout.write(
                self.style.SUCCESS(f'Superadministrador {username} creado exitosamente')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear el administrador: {str(e)}')
            )