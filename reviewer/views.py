from assignment.models import Subtask, Assignment
from .serializers import (
    SubtaskSerializer,
    CreateTeamSerializer,
    AssignmentSerializer,
)
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)
from django.db.models import Q


class CreateTeamView(CreateAPIView):
    serializer_class = CreateTeamSerializer


class CreateAssignmentView(CreateAPIView):
    serializer_class = AssignmentSerializer


class ListAssignmentView(ListAPIView):
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        return Assignment.objects.filter(
            reviewers=self.request.user
        )


class RetrieveUpdateAssignmentView(RetrieveUpdateAPIView):
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        return Assignment.objects.filter(
            reviewers=self.request.user
        )

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response.data['subtasks'] = SubtaskSerializer(
            Subtask.objects.filter(
                assignment=kwargs['pk']
            ),
            many=True,
        ).data
        return response

class CreateSubtaskView(CreateAPIView):
    serializer_class = SubtaskSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['assignment_pk'] = Assignment.objects.get(
            pk=self.kwargs['assignment_pk']
        )
        return context


class RetrieveUpdateSubtaskView(RetrieveUpdateAPIView):
    serializer_class = SubtaskSerializer

    def get_queryset(self):
        return Subtask.objects.filter(
            Q(assignment__assigned_to=self.request.user) |
            Q(assignment__assigned_to_teams__members=self.request.user)
        ).distinct()