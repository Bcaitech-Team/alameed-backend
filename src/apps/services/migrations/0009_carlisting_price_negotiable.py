# Generated by Django 4.2.17 on 2025-07-06 09:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("services", "0008_alter_vehiclecomparison_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="carlisting",
            name="price_negotiable",
            field=models.BooleanField(default=False, verbose_name="السعر قابل للتفاوض"),
        ),
    ]
