from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.db.models import Sum
from django.utils import timezone

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    # ----- Fields displayed in the transaction list -----

    list_display = (
        "id",
        "transaction_reference",
        "user",
        "card",
        "amount",
        "currency",
        "status",
        "created_at",
    )

    # ----- Filters available on the right side -----

    list_filter = (
        "status",
        "currency",
        "created_at",
    )

    # ----- Search fields -----

    search_fields = (
        "transaction_reference",
        "user__email",
        "card__last_four_digits",
    )

    # ----- Default ordering -----

    ordering = (
        "-created_at",
    )

    # ----- Fields that should not be edited manually -----

    readonly_fields = (
        "transaction_reference",
        "user",
        "card",
        "amount",
        "currency",
        "status",
        "failure_reason",
        "created_at",
        "updated_at",
    )

    # ----- Add custom admin URLs -----

    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [
            path(
                "daily-summary/",
                self.admin_site.admin_view(
                    self.daily_summary
                ),
                name="transaction_daily_summary",
            ),
        ]

        return custom_urls + urls

    # ----- Daily payment summary -----

    def daily_summary(self, request):

        today = timezone.localdate()

        transactions = Transaction.objects.filter(
            created_at__date=today
        )

        total_transactions = transactions.count()

        successful_transactions = transactions.filter(
            status="SUCCESS"
        )

        failed_transactions = transactions.filter(
            status="FAILED"
        )

        pending_transactions = transactions.filter(
            status="PENDING"
        )

        successful_amount = (
            successful_transactions.aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        context = {
            **self.admin_site.each_context(request),
            "title": "Daily Payment Summary",
            "today": today,
            "total_transactions": total_transactions,
            "successful_transactions": successful_transactions.count(),
            "failed_transactions": failed_transactions.count(),
            "pending_transactions": pending_transactions.count(),
            "successful_amount": successful_amount,
        }

        return TemplateResponse(
            request,
            "admin/transactions/daily_summary.html",
            context,
        )