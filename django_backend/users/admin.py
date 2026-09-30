from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    # ----- Fields displayed in the user list -----

    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
        "created_at",
    )

    # ----- Filters available on the right side -----

    list_filter = (
        "role",
        "is_active",
        "is_staff",
    )

    # ----- Search fields -----

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )

    # ----- Default ordering -----

    ordering = (
        "-created_at",
    )

    # ----- Fields shown when editing an existing user -----

    fieldsets = (
        (
            "Account Information",
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    # ----- Fields shown when creating a new user -----

    add_fieldsets = (
        (
            "Account Information",
            {
                "classes": (
                    "wide",
                ),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "role",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    readonly_fields = (
        "last_login",
        "created_at",
        "updated_at",
    )