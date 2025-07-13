# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.utilis import send_notification_email
from .models import CarListing


@receiver(post_save, sender=CarListing)
def send_car_listing_email(sender, instance, created, **kwargs):
    if created:
        send_notification_email(
            subject="تم إضافة سيارتك بنجاح",
            template_name="email.html",
            context={
                "message": f"""شكرًا لك على إضافة إعلان سيارتك معنا!
لقد تم إضافة إعلان سيارتك {instance.brand_model}  بنجاح إلى منصتنا.""",
            },
            recipient_list=[instance.seller_email]
        )
