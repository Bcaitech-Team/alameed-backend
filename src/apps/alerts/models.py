from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.

class Notification(models.Model):
    """
    Model to store notifications for users.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']  # Newest notifications first
