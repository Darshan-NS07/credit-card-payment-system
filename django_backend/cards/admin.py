from django.contrib import admin

from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):

    # ----- Fields displayed in the card list -----

    list_display = (
        "id",
        "user",
        "card_type",
        "cardholder_name",
        "masked_card_number",
        "last_four_digits",
        "expiry_month",
        "expiry_year",
        "created_at",
    )

    # ----- Filters available on the right side -----

    list_filter = (
        "card_type",
        "expiry_year",
    )

    # ----- Search fields -----

    search_fields = (
        "user__email",
        "cardholder_name",
        "last_four_digits",
    )

    # ----- Default ordering -----

    ordering = (
        "-created_at",
    )

    # ----- Fields that cannot be changed from admin -----

    readonly_fields = (
        "masked_card_number",
        "last_four_digits",
        "created_at",
        "updated_at",
    )