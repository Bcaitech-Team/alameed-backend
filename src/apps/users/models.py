from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):

    phone = models.CharField(max_length=15)
    user_type = models.CharField(
        choices=(
            ('admin', 'Admin'),
            ('customer', 'Customer'),
            ('staff', 'Staff'),
        ),
        default='customer',
        max_length=100,

    )

    def __str__(self):
        return f"{self.first_name} ({self.email})"

    def save(self, *args, **kwargs):
        if self.is_staff and not self.user_type == 'staff':
            self.user_type = 'staff'
        if self.is_superuser and not self.user_type == 'admin':
            self.user_type = 'admin'
        return super().save(*args, **kwargs)

