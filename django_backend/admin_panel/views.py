from django.contrib.admin.views.decorators import staff_member_required
from django.db import models
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils import timezone

from transactions.models import Transaction


@staff_member_required
def daily_payment_summary(request):

    today = timezone.localdate()

    transactions = Transaction.objects.filter(
        created_at__date=today
    )

    summary = transactions.aggregate(
        total_transactions=Count("id"),

        successful_payments=Count(
            "id",
            filter=models.Q(status="SUCCESS")
        ),

        failed_payments=Count(
            "id",
            filter=models.Q(status="FAILED")
        ),

        pending_payments=Count(
            "id",
            filter=models.Q(status="PENDING")
        ),

        successful_amount=Sum(
            "amount",
            filter=models.Q(status="SUCCESS")
        )
    )

    return JsonResponse({
        "date": str(today),
        "total_transactions": summary["total_transactions"],
        "successful_payments": summary["successful_payments"],
        "failed_payments": summary["failed_payments"],
        "pending_payments": summary["pending_payments"],
        "total_successful_amount": (
            summary["successful_amount"] or 0
        )
    })