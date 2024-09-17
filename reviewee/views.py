from assignment.models import Submission, Assignment
from assignment.permissions import IsReviewee
from .serializers import AssignmentSerializer, SubmissionSerializer, SubtaskSerializer
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


class ListAssignmentsView(ListAPIView):
    permission_classes = [IsAuthenticated, IsReviewee]
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        return Assignment.objects.filter(
            Q(assigned_to=self.request.user) |
            Q(assigned_to_teams__members=self.request.user)
        ).distinct()


class ListPendingAssignmentsView(ListAPIView):
    permission_classes = [IsAuthenticated, IsReviewee]
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        return Assignment.objects.filter(
            Q(assigned_to=self.request.user) |
            Q(assigned_to_teams__members=self.request.user),
            ~Q(submissions__reviews__status="Approved")
        ).distinct()


class RetrieveAssignmentView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsReviewee]
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        return Assignment.objects.filter(
            Q(assigned_to=self.request.user) |
            Q(assigned_to_teams__members=self.request.user)
        ).distinct()


class CreateSubmissionView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsReviewee]
    serializer_class = SubmissionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['assignment_pk'] = self.kwargs['assignment_pk']
        return context


class ListSubmissionsView(ListAPIView):
    permission_classes = [IsAuthenticated, IsReviewee]
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        assignment = Assignment.objects.get(pk=self.kwargs.get('assignment_pk'))
        return Submission.objects.filter(
            Q(submitted_by=self.request.user),
            Q(assignment=assignment)
        )

class RetrieveUpdateSubmissionView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsReviewee]
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        assignment = Assignment.objects.get(pk=self.kwargs.get('assignment_pk'))
        return Submission.objects.filter(
            Q(submitted_by=self.request.user),
            Q(assignment=assignment)
        )