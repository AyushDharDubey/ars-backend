from assignment.models import (
    Subtask,
    Assignment,
    Submission,
    Review,
    Team
)
from assignment.permissions import IsReviewer
from .serializers import (
    SubtaskSerializer,
    TeamSerializer,
    AssignmentSerializer,
    ReviewSerializer,
    SubmissionSerializer,
)
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    GenericAPIView
)
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import json
from rest_framework import status
from rest_framework.response import Response
from .utils import send_assignment_notification

User = get_user_model()


class RetrieveUpdateDestroyTeamView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = TeamSerializer


class CreateAssignmentView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = AssignmentSerializer

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        subtasks = data.pop('subtasks', None)
        assignment_serializer = self.get_serializer(data=data)
        assignment_serializer.is_valid(raise_exception=True)
        assignment_obj = assignment_serializer.save()
        assignment = assignment_serializer.data
        if subtasks is not None:
            try:
                subtasks = [{**json.loads(subtask), 'assignment': assignment_obj.pk} for subtask in subtasks]
            except json.JSONDecodeError:
                return Response(
                    {"subtasks": ["Invalid format. Must be a valid JSON array."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subtask_serializer = SubtaskSerializer(data=subtasks, many=True)
            subtask_serializer.is_valid(raise_exception=True)
            subtask_serializer.save()
            assignment['subtasks'] = subtask_serializer.data
        headers = self.get_success_headers(assignment)
        return Response(assignment, status=status.HTTP_201_CREATED, headers=headers)


class ListAssignmentView(ListAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        return Assignment.objects.filter(
            reviewers=self.request.user
        )


class RetrieveUpdateAssignmentView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        return Assignment.objects.filter(
            reviewers=self.request.user
        )


class RetrieveUpdateSubtaskView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = SubtaskSerializer

    def get_queryset(self):
        return Subtask.objects.filter(
            Q(assignment__created_by=self.request.user)
        )


class CreateReviewView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = ReviewSerializer


class ListSubmissionView(ListAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        assignment = get_object_or_404(
            Assignment,
            pk=self.kwargs['assignment_pk']
        )
        submissions = Submission.objects.filter(
            assignment=assignment
        )
        return submissions


class RetrieveUpdateReviewView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(
            submission=self.kwargs['submission_pk']
        )


class NotifyAssigneesView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]

    def post(self, request, *args, **kwargs):
        assignment = get_object_or_404(
            Assignment.objects.filter(reviewers=self.request.user),
            pk=kwargs['assignment_pk']
        )

        assignees = list(assignment.assigned_to.all())
        team_assignees = assignment.assigned_to_teams.prefetch_related('members')
        team_members = [member.email for team in team_assignees for member in team.members.all()]
        all_assignees = set([assignee.email for assignee in assignees] + team_members)

        if send_assignment_notification(
            user=self.request.user,
            recipent_list=all_assignees,
            assignment=assignment,
        ):
            return Response(
                {"message": f"Notifications sent to {len(all_assignees)} assignees successfully."},
                status=200
            )
        else:
            return Response(
                {"message": f"Try after some time."},
                status=403
            )
