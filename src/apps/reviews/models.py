from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class VehicleReview(models.Model):
    """Model for customer reviews of vehicles"""
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(_("Name"), max_length=100)
    email = models.EmailField(_("Email"))
    comment = models.TextField(_("Comment"))

    # Rating fields (1-5 stars)
    comfort_rating = models.PositiveSmallIntegerField(
        _("Comfort Rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    interior_rating = models.PositiveSmallIntegerField(
        _("Interior Rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    exterior_rating = models.PositiveSmallIntegerField(
        _("Exterior Rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    price_rating = models.PositiveSmallIntegerField(
        _("Price Rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    performance_rating = models.PositiveSmallIntegerField(
        _("Performance Rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    reliability_rating = models.PositiveSmallIntegerField(
        _("Reliability Rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )


    # Save name and email preference
    save_info = models.BooleanField(
        _("Save user info"),
        default=False,
        help_text=_("Save name, email, and website for next time")
    )

    # Review metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Vehicle Review")
        verbose_name_plural = _("Vehicle Reviews")

    def __str__(self):
        return f"Review for {self.vehicle} by {self.name}"

    @property
    def average_rating(self):
        """Calculate the average rating from all rating fields"""
        ratings = [
            self.comfort_rating,
            self.interior_rating,
            self.exterior_rating,
            self.price_rating,
            self.performance_rating,
            self.reliability_rating
        ]
        return sum(ratings) / len(ratings)