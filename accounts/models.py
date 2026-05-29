from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("superadmin", "SuperAdmin"),
        ("admin", "Admin"),
        ("salesperson", "SalesPerson"),
    )

    personID = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, blank=True, default="")
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="salesperson",
    )
    mobile_number = models.CharField(max_length=15, blank=True, default="")
    alternative_contact_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
    )
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
    )
    is_profile_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.personID} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.personID
        super().save(*args, **kwargs)
