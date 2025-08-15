from django.apps import AppConfig



class RentalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.apps.rental'

    def ready(self):
        from src.apps.rental.models import create_rental_perms
        create_rental_perms()
