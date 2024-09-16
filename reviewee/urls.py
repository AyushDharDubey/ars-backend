from django.urls import path
from .views import (
    ListPendingAssignmentsView,
    ListAssignmentsView,
    CreateSubmissionView,
    RetrieveAssignmentView
)


urlpatterns = [
    path('assignments/', ListAssignmentsView.as_view()),
    path('assignments/pending/', ListPendingAssignmentsView.as_view()),
    path('assignment/<int:pk>/', RetrieveAssignmentView.as_view()),
    path('assignment/<int:assignment_pk>/submit/', CreateSubmissionView.as_view()),
]
