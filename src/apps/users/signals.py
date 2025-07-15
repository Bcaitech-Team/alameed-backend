from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from src.apps.alerts.models import Notification

User = get_user_model()


@receiver(post_save, sender=User)
def send_welcome_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance,
            title="مرحبًا بك!",
            message=(
                f"مرحبًا {instance.get_full_name() or instance.username}!\n"
                "شكرًا لانضمامك إلينا. نتمنى لك تجربة رائعة معنا.\n"
                "لا تتردد في التواصل معنا لأي استفسار!"
            )
        )
