from django.db import models
from django.contrib.auth import get_user_model
import uuid, os

User = get_user_model()

def upload_to(attachment, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/', filename)


class Team(models.Model):
    members = models.ManyToManyField(User, related_name="teams")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class File(models.Model):
    file = models.FileField(upload_to=upload_to)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    files = models.ManyToManyField(File, blank=True)
    due_date = models.DateTimeField()
    assigned_to = models.ManyToManyField(User, blank=True, related_name="reviewee_assignments")
    assigned_to_teams = models.ManyToManyField(Team, blank=True, related_name="assignments")
    reviewers = models.ManyToManyField(User, blank=True, related_name="reviewer_assignments")
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


class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions"
    )
    submitted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="submissions"
    )
    is_group_submission = models.BooleanField(default=False)
    files = models.ManyToManyField(File, blank=True)
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
