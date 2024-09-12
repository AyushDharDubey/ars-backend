from django.urls import path
from .views import (
    PendingAssignmentsView,
    ListAssignmentsView
)


urlpatterns = [
    path('assignments/', ListAssignmentsView.as_view()),
    path('assignments/pending/', PendingAssignmentsView.as_view()),
]
