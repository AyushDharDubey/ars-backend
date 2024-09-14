from django.urls import path
from .views import (
    PendingAssignmentsView,
    ListAssignmentsView,
    SubmissionView
)


urlpatterns = [
    path('assignments/', ListAssignmentsView.as_view()),
    path('assignments/pending/', PendingAssignmentsView.as_view()),
    path('assignment/<int:assignment_pk>/submit/', SubmissionView.as_view()),
]
