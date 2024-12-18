from django.urls import path
from .views import (
    CreateTeamView,
    ListTeamView,
    RetrieveUpdateDestroyTeamView,
    CreateAssignmentView,
    RetrieveUpdateAssignmentView,
    ListAssignmentView,
    RetrieveUpdateSubtaskView,
    CreateReviewView,
    ListSubmissionView,
    RetrieveUpdateReviewView,
    ListRevieweeView
)

urlpatterns = [
    path('list_reviewees/', ListRevieweeView.as_view(), name='list-reviewees'),
    path('team/', CreateTeamView.as_view(), name='reviewer-create-team'),
    path('list_teams/', ListTeamView.as_view(), name='reviewer-list-team'),
    path('team/<int:pk>/', RetrieveUpdateDestroyTeamView.as_view(), name='reviewer-retrieve-update-destroy-team'),
    path('create_assignment/', CreateAssignmentView.as_view(), name='reviewer-create-assignment'),
    path('assignments/', ListAssignmentView.as_view(), name='reviewer-list-assignments'),
    path('assignment/<int:pk>/', RetrieveUpdateAssignmentView.as_view(), name='reviewer-retrieve-update-assignment'),
    path('assignment/<int:assignment_pk>/subtask/<int:pk>/', RetrieveUpdateSubtaskView.as_view(), name='reviewer-retrieve-update-subtask'),
    path('assignment/<int:assignment_pk>/submissions/', ListSubmissionView.as_view(), name='reviewer-list-submissions'),
    path('submission/<int:submission_pk>/create_review/', CreateReviewView.as_view(), name='reviewer-create-review'),
    path('submission/<int:submission_pk>/review/<int:pk>/', RetrieveUpdateReviewView.as_view(), name='reviewer-retrieve-update-review'),
]
