from assignment.models import Submission, Review, Assignment
from .serializers import AssignmentSerializer
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView
from django.db.models import Q


class ListAssignmentsView(ListAPIView):
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        return Assignment.objects.filter(
            Q(assigned_to=self.request.user) |
            Q(assigned_to_teams__members=self.request.user)
        ).distinct()


class PendingAssignmentsView(ListAPIView):
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        assigned_to_user = Assignment.objects.filter(
            Q(assigned_to=self.request.user) |
            Q(assigned_to_teams__members=self.request.user)
        ).distinct()
        
        pending_assignments = assigned_to_user.exclude(
            submissions__reviews__status="Approved"
        ).distinct()

        return pending_assignments
