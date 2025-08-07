from django.apps import AppConfig


class DistribuidorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Distribuidor'

    def ready(self):
        import Distribuidor.signals  # importa tu archivo de signals