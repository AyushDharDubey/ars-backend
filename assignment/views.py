from .models import Team
from assignment.permissions import IsReviewee, IsAdmin
from .serializers import TeamSerializer, RevieweeSerializer
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from .models import Message

User = get_user_model()

class ListTeamView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer
    queryset = Team.objects.all()


class ListRevieweeView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RevieweeSerializer
    queryset = User.objects.filter(groups__name='Reviewee')


class CreateTeamView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = TeamSerializer


class TeamMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, team_pk):
        try:
            team = Team.objects.get(pk=team_pk)
        except Team.DoesNotExist:
            return Response({"error": "Team not found."}, status=404)

        if not request.user in team.members.all():
            return Response({"error": "You are not a member of this team."}, status=403)

        page = int(request.query_params.get("page", 1))
        messages = team.messages.all().order_by("-created_at")
        paginator = Paginator(messages, 20)  # Paginate 20 messages per page
        paginated_messages = paginator.page(page)

        return Response({
            "messages": [
                {
                    "username": message.user.username,
                    "content": message.content,
                    "timestamp": message.created_at,
                } for message in reversed(paginated_messages)
            ],
            "has_next": paginated_messages.has_next(),
        })
