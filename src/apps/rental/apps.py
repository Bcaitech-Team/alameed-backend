from django.apps import AppConfig


class RentalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.apps.rental'

    def ready(self):
        # Import the signals module to ensure that the signal handlers are registered
        pass
