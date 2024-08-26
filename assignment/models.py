from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to="uploads/assignment/", blank=True, null=True)
    due_date = models.DateTimeField()
    reviewers = models.ManyToManyField(User, related_name="reviewer_assignments")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_assignments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Subtask(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="subtasks"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Team(models.Model):
    members = models.ManyToManyField(User, related_name="teams")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AssignmentAllocation(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="allocations"
    )
    allocated_to = models.ManyToManyField(
        User, blank=True, related_name="allocated_assignments"
    )
    team = models.ManyToManyField(Team, related_name="allocated_assignments", blank=True)
    reviewer = models.ManyToManyField(User, related_name="assignment_allocations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions"
    )
    submitted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="submissions"
    )
    is_group_submission = models.BooleanField(default=False)
    file = models.FileField(upload_to="uploads/submissions/", blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Review(models.Model):
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="reviews"
    )
    comments = models.TextField()
    status = models.CharField(
        max_length=17,
        choices=[
            ("Approved", "Approved"),
            ("Rejected", "Rejected"),
            ("Changes Suggested", "Changes Suggested"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
