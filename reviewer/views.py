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
    RevieweeSerializer
)
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import json
from rest_framework import status
from rest_framework.response import Response


User = get_user_model()

class ListRevieweeView(ListAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = RevieweeSerializer

    def get_queryset(self):
        return User.objects.filter(
            groups=Group.objects.get(name='Reviewee')
        )


class CreateTeamView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = TeamSerializer


class ListTeamView(ListAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = TeamSerializer
    queryset = Team.objects.all()


class RetrieveUpdateDestroyTeamView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = TeamSerializer


class CreateAssignmentView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = AssignmentSerializer

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        subtasks = data.pop('subtasks', '[]')
        assignment_serializer = self.get_serializer(data=data)
        assignment_serializer.is_valid(raise_exception=True)
        assignment_obj = assignment_serializer.save()
        assignment = assignment_serializer.data
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