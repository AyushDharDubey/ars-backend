from django.urls import path
from .views import (
    ListPendingAssignmentsView,
    ListAssignmentsView,
    CreateSubmissionView,
    RetrieveAssignmentView,
    ListSubmissionsView,
    RetrieveUpdateSubmissionView
)

urlpatterns = [
    path('assignments/', ListAssignmentsView.as_view(), name='reviewee-list-assignments'),
    path('assignments/pending/', ListPendingAssignmentsView.as_view(), name='reviewee-pending-assignments'),
    path('assignment/<int:pk>/', RetrieveAssignmentView.as_view(), name='reviewee-retrieve-assignment'),
    path('assignment/<int:assignment_pk>/submit/', CreateSubmissionView.as_view(), name='reviewee-create-submission'),
    path('assignment/<int:assignment_pk>/submissions/', ListSubmissionsView.as_view(), name='reviewee-list-submissions'),
    path('assignment/<int:assignment_pk>/submission/<int:pk>', RetrieveUpdateSubmissionView.as_view(), name='reviewee-retrieve-update-submission'),
]
