from datetime import date

from rest_framework import serializers

from .models import Card


class CardSerializer(serializers.ModelSerializer):

    card_number = serializers.CharField(
        write_only=True,
        min_length=13,
        max_length=19
    )

    class Meta:
        model = Card

        fields = [
            "id",
            "card_type",
            "cardholder_name",
            "card_number",
            "masked_card_number",
            "last_four_digits",
            "expiry_month",
            "expiry_year",
            "created_at",
            "updated_at"
        ]

        read_only_fields = [
            "id",
            "masked_card_number",
            "last_four_digits",
            "created_at",
            "updated_at"
        ]

    def validate_card_number(self, value):

        value = value.replace(" ", "").replace("-", "")

        if not value.isdigit():
            raise serializers.ValidationError(
                "Card number must contain only digits."
            )

        if not 13 <= len(value) <= 19:
            raise serializers.ValidationError(
                "Card number must contain between 13 and 19 digits."
            )

        if not self.luhn_check(value):
            raise serializers.ValidationError(
                "Invalid card number."
            )

        return value

    def validate_cardholder_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Cardholder name cannot be empty."
            )

        return value

    def validate_expiry_month(self, value):

        if not 1 <= value <= 12:
            raise serializers.ValidationError(
                "Expiry month must be between 1 and 12."
            )

        return value

    def validate_expiry_year(self, value):

        current_year = date.today().year

        if value < current_year:
            raise serializers.ValidationError(
                "Card has expired."
            )

        if value > current_year + 20:
            raise serializers.ValidationError(
                "Invalid expiry year."
            )

        return value

    def validate(self, data):

    # ----- Reject unexpected fields such as CVV -----

        allowed_fields = {
        "card_type",
        "cardholder_name",
        "card_number",
        "expiry_month",
        "expiry_year",
       }

        unexpected_fields = set(self.initial_data.keys()) - allowed_fields

        if unexpected_fields:

            raise serializers.ValidationError(
            {
                "error": (
                    "Unexpected field(s): "
                    + ", ".join(sorted(unexpected_fields))
                )
            }
        )

    # ----- Validate card expiry -----

        month = data["expiry_month"]
        year = data["expiry_year"]
        today = date.today()

        if year == today.year and month < today.month:

           raise serializers.ValidationError(
            {
                "expiry_month": "Card has expired."
            }
        )

        return data

    @staticmethod
    def luhn_check(card_number):

        digits = [
            int(digit)
            for digit in card_number
        ]

        checksum = 0
        parity = len(digits) % 2

        for index, digit in enumerate(digits):

            if index % 2 == parity:
                digit *= 2

                if digit > 9:
                    digit -= 9

            checksum += digit

        return checksum % 10 == 0

    def create(self, validated_data):

        card_number = validated_data.pop("card_number")

        last_four_digits = card_number[-4:]

        masked_card_number = (
            "*" * (len(card_number) - 4)
            + last_four_digits
        )

        user = self.context["request"].user

        card = Card.objects.create(
            user=user,
            masked_card_number=masked_card_number,
            last_four_digits=last_four_digits,
            **validated_data
        )

        return card