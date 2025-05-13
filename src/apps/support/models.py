import mimetypes

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils import timezone


# Create your models here.
class ChatFile(models.Model):
    file = models.FileField(upload_to="support/files/")
    mimetype = models.CharField(null=True, blank=True, max_length=100)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if not self.mimetype:
            self.mimetype = self.get_mimetype()

        return super().save(*args, **kwargs)

    def get_mimetype(self):
        return mimetypes.guess_type(self.file.name)[0]

    def file_name(self):
        return self.file.name[self.file.name.rfind("/") + 1:]


class Ticket(models.Model):
    """
    Support ticket model for customer inquiries
    """
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    subject = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.subject}"

    def resolve(self):
        """Mark the ticket as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()


class ChatMessage(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    files = models.ManyToManyField("ChatFile", blank=True)
    room = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    index = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room} - {self.message} {self.date}"

    class Meta:
        ordering = ("date",)
        unique_together = ("room", "index")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Retrieve the current maximum index value within the room
            max_index = ChatMessage.objects.filter(room=self.room).aggregate(models.Max("index"))["index__max"] or 0

            # Increment the index by 1 using F() expression and save the object
            self.index = max_index + 1
            super().save(*args, **kwargs)

    def last_message(self):
        try:
            return ChatMessage.objects.filter(room=self.room, index__lte=self.index - 1, deleted=False).last()
        except Exception:
            return

    def next_messages(self):
        messages = ChatMessage.objects.filter(room=self.room, index__gt=self.index, deleted=False)

        end = messages.exclude(user=self.user).filter(index__gt=self.index)
        if end.exists():
            messages = messages.filter(index__lt=end[0].index)
        return messages


class ContactMessage(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Phone")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.created_at.strftime('%Y-%m-%d')}"
