from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from assignment.models import Assignment, Team, File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import Group
from django.test import override_settings

User = get_user_model()

class AssignmentAPITest(APITestCase):
    def setUp(self):
        self.reviewee = User.objects.create_user(username="reviewee", password="123", email="reviewee@gmail.com")
        self.reviewer = User.objects.create_user(username="reviewer", password="123", email="reviewer@gmail.com")
        reviewee = Group.objects.create(name="Reviewee")
        reviewer = Group.objects.create(name="Reviewer")
        self.reviewee.groups.add(reviewee)
        self.reviewer.groups.add(reviewer)
        self.reviewee.is_active=1
        self.reviewer.is_active=1
        self.reviewee.save()
        self.reviewer.save()

        self.team1 = Team.objects.create()
        self.team1.members.add(self.reviewee)

        self.client = APIClient()
        self.client.login(username='reviewer', password='123')

        self.test_file = SimpleUploadedFile(
            "test_file.pdf", b"This is a test file content", content_type="application/pdf"
        )

    def test_create_assignment(self):
        """
        Ensure we can create an assignment with file uploads.
        """
        url = reverse('reviewer-create-assignment')

        data = {
            'title': 'Test Assignment',
            'description': 'This is a test assignment description.',
            'due_date': (now() + timedelta(days=7)).isoformat(),
            'assigned_to': [self.reviewee.id],
            'assigned_to_teams': [self.team1.id],
            'reviewers': [self.reviewer.id],
            'attachments': [self.test_file, ]
        }

        response = self.client.post(url, data, format='multipart', HTTP_ACCEPT='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assignment.objects.count(), 1)

        assignment = Assignment.objects.first()
        self.assertEqual(assignment.title, 'Test Assignment')
        self.assertEqual(assignment.files.count(), 1)

    def test_create_assignment_unauthenticated(self):
        """
        Test creating an assignment without authentication.
        """
        self.client.logout()

        url = reverse('reviewer-create-assignment')
        data = {
            'title': 'Unauthenticated Assignment',
            'description': 'This should fail.',
            'due_date': (now() + timedelta(days=7)).isoformat(),
            'assigned_to': [self.reviewee.id],
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
