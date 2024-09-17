from django.urls import path
from .views import (
    ListPendingAssignmentsView,
    ListAssignmentsView,
    CreateSubmissionView,
    RetrieveAssignmentView
)

urlpatterns = [
    path('assignments/', ListAssignmentsView.as_view(), name='reviewee-list-assignments'),
    path('assignments/pending/', ListPendingAssignmentsView.as_view(), name='reviewee-pending-assignments'),
    path('assignment/<int:pk>/', RetrieveAssignmentView.as_view(), name='reviewee-retrieve-assignment'),
    path('assignment/<int:assignment_pk>/submit/', CreateSubmissionView.as_view(), name='reviewee-create-submission'),
]
