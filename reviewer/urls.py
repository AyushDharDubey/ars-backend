from django.urls import path
from .views import (
    CreateTeamView,
    CreateAssignmentView,
    RetrieveUpdateAssignmentView,
    ListAssignmentView,
    CreateSubtaskView,
    RetrieveUpdateSubtaskView,
)

urlpatterns = [
    path('create_team/', CreateTeamView.as_view()),
    path('create_assignment/', CreateAssignmentView.as_view()),
    path('assignments/', ListAssignmentView.as_view()),
    path('assignment/<int:pk>/', RetrieveUpdateAssignmentView.as_view()),
    path('assignment/<int:assignment_pk>/create_subtask/', CreateSubtaskView.as_view()),
    path('assignment/<int:assignment_pk>/subtask/<int:pk>/', RetrieveUpdateSubtaskView.as_view()),
]
