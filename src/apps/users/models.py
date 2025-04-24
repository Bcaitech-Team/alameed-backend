from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):

    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} ({self.email})"
