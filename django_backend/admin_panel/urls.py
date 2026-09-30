from django.urls import path

from .views import daily_payment_summary


urlpatterns = [
    path(
        "daily-summary/",
        daily_payment_summary,
        name="daily_payment_summary"
    ),
]