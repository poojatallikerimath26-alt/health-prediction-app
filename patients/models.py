from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


def validate_not_future_date(value):
    """A date of birth can never be in the future."""
    if value > date.today():
        raise ValidationError("Date of birth cannot be in the future.")


class PatientRecord(models.Model):
    """
    One blood-test record for one patient.
    'remarks' is never typed by the user -- it is generated automatically
    by the ML prediction engine whenever a record is saved.
    """

    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(validators=[validate_not_future_date])
    email = models.EmailField()

    glucose = models.FloatField(
        help_text="mg/dL",
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
    )
    haemoglobin = models.FloatField(
        help_text="g/dL",
        validators=[MinValueValidator(1), MaxValueValidator(30)],
    )
    cholesterol = models.FloatField(
        help_text="mg/dL",
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
    )

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["full_name", "date_of_birth", "email"],
                name="unique_patient_record",
            )
        ]

    def __str__(self):
        return f"{self.full_name} ({self.date_of_birth})"