# Generated by Django 4.2.17 on 2025-07-07 23:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rental", "0005_alter_rental_customer_data"),
    ]

    operations = [
        migrations.CreateModel(
            name="Installment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("due_date", models.DateField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("is_paid", models.BooleanField(default=False)),
                (
                    "rental",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="installments",
                        to="rental.rental",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="installments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
