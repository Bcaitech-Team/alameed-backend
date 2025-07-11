from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Q

from src.apps.vehicles.models import Vehicle


class CustomerData(models.Model):
    first_name = models.CharField(max_length=100, default="")
    middle_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    phone_number = models.CharField(max_length=20)
    id_number = models.CharField(max_length=50)
    nationality = models.CharField(max_length=100)
    license_front_photo = models.ImageField(upload_to='licenses/front/')
    license_back_photo = models.ImageField(upload_to='licenses/back/')
    id_front_photo = models.ImageField(upload_to='ids/front/')
    id_back_photo = models.ImageField(upload_to='ids/back/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Installment(models.Model):
    rental = models.ForeignKey('Rental', on_delete=models.CASCADE, related_name='installments')
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='installments')

    def __str__(self):
        return f"Installment for {self.rental} due on {self.due_date}"


class RentalStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    ACTIVE = 'active', 'Active'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'



class Rental(models.Model):
    customer_data = models.ForeignKey(CustomerData, on_delete=models.CASCADE, related_name='rentals', null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='rentals')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='created_rentals')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=RentalStatus.choices,
        default=RentalStatus.PENDING
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inspection_form = models.FileField(upload_to='inspections/', null=True, blank=True)

    def __str__(self):
        return f"{self.customer_data} - {self.vehicle} ({self.start_date} to {self.end_date})"

    def save(self, *args, **kwargs):
        delta = self.end_date - self.start_date
        total_days = delta.days + (1 if delta.seconds > 0 else 0)

        if not self.total_price and self.vehicle and self.start_date and self.end_date:
            # Try to find a matching price tier first
            price_tier = self.vehicle.price_tiers.filter(
                min_days__lte=total_days
            ).filter(
                Q(max_days__gte=total_days) | Q(max_days__isnull=True)
            ).order_by('min_days').first()

            if price_tier:
                self.total_price = price_tier.price_per_day * total_days
            else:
                self.total_price = self.vehicle.price * total_days

        vehicle = self.vehicle

        # If staff, auto-activate rental
        if self.user.is_staff:
            self.status = RentalStatus.ACTIVE

        # If this rental is newly becoming active
        is_new = self.pk is None
        already_active = not is_new and Rental.objects.filter(pk=self.pk, status=RentalStatus.ACTIVE).exists()

        if (is_new or not already_active) and self.status == RentalStatus.ACTIVE:
            if vehicle.available_units > 0:
                vehicle.available_units -= 1

                if vehicle.available_units <= 0:
                    vehicle.status = 'rented'
                    vehicle.is_available = False

                vehicle.save()
            else:
                raise ValueError("No available units left for this vehicle.")

        super().save(*args, **kwargs)

        # Create installments if not staff and not already created
        if not self.user.is_staff and not self.installments.exists():
            full_months = total_days // 30
            remaining_days = total_days % 30

            with transaction.atomic():
                if full_months == 0:
                    Installment.objects.create(
                        rental=self,
                        due_date=self.start_date.date(),
                        amount=self.total_price,
                        user=self.user,
                    )
                else:
                    monthly_amount = (self.total_price / total_days) * 30
                    remaining_amount = self.total_price - (monthly_amount * full_months)

                    due_date = self.start_date
                    for i in range(full_months):
                        Installment.objects.create(
                            rental=self,
                            due_date=(due_date + relativedelta(months=i)).date(),
                            amount=monthly_amount,
                            user=self.user,
                        )
                    if remaining_days > 0:
                        Installment.objects.create(
                            rental=self,
                            due_date=(due_date + relativedelta(months=full_months)).date(),
                            amount=remaining_amount,
                            user=self.user,
                        )
