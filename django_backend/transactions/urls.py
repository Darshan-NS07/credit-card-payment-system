from django.urls import path

from .views import (
    TransactionCSVExportView,
    TransactionDetailView,
    TransactionListView,
)


urlpatterns = [
    path(
        "",
        TransactionListView.as_view(),
        name="transaction_list"
    ),

    path(
        "export-csv/",
        TransactionCSVExportView.as_view(),
        name="transaction_csv_export"
    ),

    path(
        "<int:transaction_id>/",
        TransactionDetailView.as_view(),
        name="transaction_detail"
    ),
]