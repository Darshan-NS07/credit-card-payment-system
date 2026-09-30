import csv

from django.http import HttpResponse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        transactions = Transaction.objects.filter(
            user=request.user
        ).select_related("card").order_by("-created_at")

        # ----- Filter by transaction status -----

        status_filter = request.query_params.get("status")

        if status_filter:
            transactions = transactions.filter(
                status=status_filter.upper()
            )

        # ----- Filter by minimum amount -----

        min_amount = request.query_params.get("min_amount")

        if min_amount:
            transactions = transactions.filter(
                amount__gte=min_amount
            )

        # ----- Filter by maximum amount -----

        max_amount = request.query_params.get("max_amount")

        if max_amount:
            transactions = transactions.filter(
                amount__lte=max_amount
            )

        # ----- Filter by start date -----

        start_date = request.query_params.get("start_date")

        if start_date:
            transactions = transactions.filter(
                created_at__date__gte=start_date
            )

        # ----- Filter by end date -----

        end_date = request.query_params.get("end_date")

        if end_date:
            transactions = transactions.filter(
                created_at__date__lte=end_date
            )

        serializer = TransactionSerializer(
            transactions,
            many=True
        )

        return Response(
            {
                "transactions": serializer.data
            },
            status=status.HTTP_200_OK
        )

class TransactionDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, transaction_id):

        try:
            transaction = Transaction.objects.select_related(
                "card"
            ).get(
                id=transaction_id,
                user=request.user
            )

        except Transaction.DoesNotExist:

            return Response(
                {
                    "error": "Transaction not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TransactionSerializer(transaction)

        return Response(
            {
                "transaction": serializer.data
            },
            status=status.HTTP_200_OK
        )        


class TransactionCSVExportView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # ----- Check whether the logged-in user is an admin -----

        if request.user.role != "ADMIN":

            return Response(
                {
                    "error": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # ----- Get all transactions -----

        transactions = Transaction.objects.select_related(
            "card",
            "user"
        ).order_by("-created_at")

        # ----- Create CSV response -----

        response = HttpResponse(
            content_type="text/csv"
        )

        response["Content-Disposition"] = (
            'attachment; filename="transactions.csv"'
        )

        writer = csv.writer(response)

        # ----- Add CSV header -----

        writer.writerow([
            "Transaction ID",
            "Transaction Reference",
            "User Email",
            "Card",
            "Amount",
            "Currency",
            "Status",
            "Failure Reason",
            "Created At",
            "Updated At"
        ])

        # ----- Add transaction data -----

        for transaction in transactions:

            writer.writerow([
                transaction.id,
                transaction.transaction_reference,
                transaction.user.email,
                transaction.card.masked_card_number
                if transaction.card
                else "",
                transaction.amount,
                transaction.currency,
                transaction.status,
                transaction.failure_reason or "",
                transaction.created_at,
                transaction.updated_at
            ])

        return response    