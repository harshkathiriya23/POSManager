from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "personID",
        "username",
        "name",
        "email",
        "role",
        "is_profile_completed",
        "is_staff",
        "is_active",
    )
    list_editable = ("is_active",)
    list_filter = ("role", "is_profile_completed", "is_staff", "is_active")
    search_fields = ("personID", "username", "name", "email")
    ordering = ("personID",)

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "FMCG Profile",
            {
                "fields": (
                    "personID",
                    "name",
                    "role",
                    "mobile_number",
                    "alternative_contact_number",
                    "address",
                    "profile_picture",
                    "is_profile_completed",
                ),
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "FMCG Profile",
            {
                "fields": (
                    "personID",
                    "name",
                    "role",
                    "mobile_number",
                ),
            },
        ),
    )
