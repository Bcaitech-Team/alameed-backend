# signals.py

# @receiver(post_save, sender=Rental)
# def send_next_installment_notification(sender, instance, created, **kwargs):
#     if created:
#         next_installment = instance.installments.filter(
#         ).order_by('due_date').first()
#         print(f"Next installment: {next_installment}")
#
#         if next_installment:
#             Notification.objects.create(
#                 user=instance.user,
#                 title="تم تأجير المركبة",
#                 message=(
#                     f"تم تأجير المركبة بنجاح.\n"
#                     f"يرجى العلم أن القسط الأول مستحق بتاريخ {next_installment.due_date} "
#                     f"بمبلغ قدره {next_installment.amount} دينار.\n"
#                     "شكرًا لاختياركم خدمتنا ونتمنى لكم تجربة قيادة آمنة."
#                 )
#             )
