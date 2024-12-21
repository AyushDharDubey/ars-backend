from django.urls import path
from .views import (
    ListTeamView,
    ListRevieweeView,
    CreateTeamView,
    TeamMessagesView
)

urlpatterns = [
    path('list_reviewees/', ListRevieweeView.as_view(), name='list-reviewees'),
    path('list_teams/', ListTeamView.as_view(), name='list-team'),
    path('create_team/', CreateTeamView.as_view(), name='create-team'),
    path('team/<int:team_pk>/messages/', TeamMessagesView.as_view(), name='create-team'),
]
