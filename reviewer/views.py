from assignment.models import (
    Subtask,
    Assignment,
    Submission,
    Review,
)
from assignment.permissions import IsReviewer
from .serializers import (
    SubtaskSerializer,
    TeamSerializer,
    AssignmentSerializer,
    ReviewSerializer,
    SubmissionSerializer
)
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated


class CreateTeamView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = TeamSerializer


class CreateAssignmentView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = AssignmentSerializer


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


class CreateSubtaskView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = SubtaskSerializer


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