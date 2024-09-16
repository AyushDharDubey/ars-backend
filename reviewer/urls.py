from django.urls import path
from .views import (
    CreateTeamView,
    CreateAssignmentView,
    RetrieveUpdateAssignmentView,
    ListAssignmentView,
    CreateSubtaskView,
    RetrieveUpdateSubtaskView,
    CreateReviewView,
    ListSubmissionView,
    RetrieveUpdateReviewView,
)

urlpatterns = [
    path('create_team/', CreateTeamView.as_view()),
    path('create_assignment/', CreateAssignmentView.as_view()),
    path('assignments/', ListAssignmentView.as_view()),
    path('assignment/<int:pk>/', RetrieveUpdateAssignmentView.as_view()),
    path('assignment/<int:assignment_pk>/create_subtask/', CreateSubtaskView.as_view()),
    path('assignment/<int:assignment_pk>/subtask/<int:pk>/', RetrieveUpdateSubtaskView.as_view()),
    path('assignment/<int:assignment_pk>/submissions/', ListSubmissionView.as_view()),
    path('submission/<int:submission_pk>/review/', CreateReviewView.as_view()),
    path('submission/<int:submission_pk>/review/<int:pk>/', RetrieveUpdateReviewView.as_view()),
]
