from assignment.models import (
    Subtask,
    Assignment,
    Submission,
    Review,
)
from assignment.permissions import IsReviewer
from .serializers import (
    SubtaskSerializer,
    CreateTeamSerializer,
    AssignmentSerializer,
    ReviewSerializer,
    SubmissionSerializer
)
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated


class CreateTeamView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = CreateTeamSerializer


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
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = SubtaskSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['assignment_pk'] = self.kwargs['assignment_pk']
        return context


class RetrieveUpdateSubtaskView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = SubtaskSerializer

    def get_queryset(self):
        return Subtask.objects.filter(
            Q(assignment__assigned_to=self.request.user) |
            Q(assignment__assigned_to_teams__members=self.request.user)
        ).distinct()


class CreateReviewView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = ReviewSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['submission_pk'] = self.kwargs['submission_pk']
        return context


class ListSubmissionView(ListAPIView):
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        assignment = Assignment.objects.get(pk=self.kwargs['assignment_pk'])
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