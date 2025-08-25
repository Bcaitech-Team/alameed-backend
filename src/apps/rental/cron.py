from datetime import timedelta

from django.utils import timezone

from src.apps.alerts.models import Notification
from src.apps.rental.models import Installment, Rental


def send_installment_notifications():
    today = timezone.now().date()
    reminders = [1, 3]  # 1 and 3 days before

    installments = Installment.objects.filter(is_paid=False)

    for installment in installments:
        due_date = installment.due_date

        # On the due date
        if due_date == today:
            create_notification(installment, due_date, "اليوم")

        # Days before
        for r in reminders:
            if due_date == today + timedelta(days=r):
                create_notification(installment, due_date, f"بعد {r} أيام")


def send_rental_return_reminders():
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    rentals = Rental.objects.filter(end_date__date=tomorrow, status="active")

    for rental in rentals:
        create_notification(
            rental.user,
            "تذكير بإرجاع السيارة",
            f"عزيزي العميل، تنتهي مدة تأجير سيارتك ({rental.vehicle}) بتاريخ {rental.end_date.date()}.\n"
            "يرجى إعادة السيارة في الموعد المحدد لتجنب أي رسوم إضافية.\n"
            "شكرًا لتعاملكم معنا."
        )


def create_notification(installment, due_date, when_text):
    Notification.objects.create(
        user=installment.user,
        title="تذكير بدفع القسط",
        message=(
            f"لديك قسط مستحق {when_text} بتاريخ {due_date} "
            f"بمبلغ {installment.amount} دينار.\n"
            "يرجى التأكد من الدفع في الوقت المحدد لتجنب أي رسوم إضافية."
        )
    )
    print(f"✅ Notification sent to {installment.user} for {due_date}")
