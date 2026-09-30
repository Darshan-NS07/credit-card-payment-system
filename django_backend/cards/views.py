from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Card
from .serializers import CardSerializer


class CardListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        cards = Card.objects.filter(
            user=request.user
        ).order_by("-created_at")

        serializer = CardSerializer(
            cards,
            many=True
        )

        return Response(
            {
                "cards": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):

        serializer = CardSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        if serializer.is_valid():
            card = serializer.save()

            return Response(
                {
                    "message": "Card added successfully.",
                    "card": CardSerializer(card).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class CardDeleteView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, card_id):

        try:
            card = Card.objects.get(
                id=card_id,
                user=request.user
            )

        except Card.DoesNotExist:
            return Response(
                {
                    "error": "Card not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        card.delete()

        return Response(
            {
                "message": "Card deleted successfully."
            },
            status=status.HTTP_200_OK
        )        