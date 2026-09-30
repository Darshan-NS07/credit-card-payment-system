from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):

    card_masked_number = serializers.CharField(
        source="card.masked_card_number",
        read_only=True
    )

    class Meta:

        model = Transaction

        fields = [
            "id",
            "transaction_reference",
            "card",
            "card_masked_number",
            "amount",
            "currency",
            "status",
            "failure_reason",
            "created_at",
            "updated_at"
        ]

        read_only_fields = [
            "id",
            "transaction_reference",
            "card",
            "card_masked_number",
            "amount",
            "currency",
            "status",
            "failure_reason",
            "created_at",
            "updated_at"
        ]