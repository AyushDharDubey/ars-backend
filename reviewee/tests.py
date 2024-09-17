from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assignment.models import Assignment, Subtask, Review, Submission
from django.utils import timezone
from django.contrib.auth.models import Group

User = get_user_model()


class RevieweeAssignmentTestCase(APITestCase):

    def setUp(self):
        self.reviewer_group = Group.objects.create(name='Reviewer')
        self.reviewee_group = Group.objects.create(name='Reviewee')

        self.reviewer = User.objects.create_user(username='reviewer', password='123', email='reviewer@gmail.com')
        self.reviewer.groups.add(self.reviewer_group)

        self.reviewee = User.objects.create_user(username='reviewee', password='123', email='reviewee@gmail.com')
        self.reviewee.groups.add(self.reviewee_group)

        self.assignment = Assignment.objects.create(
            title="Test Assignment for Reviewee",
            description="Assignment for reviewee description",
            due_date=timezone.now() + timezone.timedelta(days=7),
            created_by=self.reviewer
        )
        self.assignment.reviewers.add(self.reviewer)
        self.assignment.assigned_to.add(self.reviewee)

    def test_list_assignments(self):
        self.client.force_authenticate(user=self.reviewee)
        url = reverse('reviewee-list-assignments')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Test Assignment for Reviewee")

    def test_retrieve_assignment(self):
        self.client.force_authenticate(user=self.reviewee)
        url = reverse('reviewee-retrieve-assignment', args=[self.assignment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.assignment.title)


class RevieweeSubmissionTestCase(APITestCase):

    def setUp(self):
        self.reviewer_group = Group.objects.create(name='Reviewer')
        self.reviewee_group = Group.objects.create(name='Reviewee')

        self.reviewer = User.objects.create_user(username='reviewer', password='123', email='reviewer@gmail.com')
        self.reviewer.groups.add(self.reviewer_group)

        self.reviewee = User.objects.create_user(username='reviewee', password='123', email='reviewee@gmail.com')
        self.reviewee.groups.add(self.reviewee_group)

        self.assignment = Assignment.objects.create(
            title="Test Assignment for Reviewee",
            description="Assignment for reviewee description",
            due_date=timezone.now() + timezone.timedelta(days=7),
            created_by=self.reviewer
        )
        self.assignment.reviewers.add(self.reviewer)
        self.assignment.assigned_to.add(self.reviewee)

    def test_create_submission(self):
        self.client.force_authenticate(user=self.reviewee)
        url = reverse('reviewee-create-submission', args=[self.assignment.id])
        data = {
            'description': 'My Submission',
            'attachments': []
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Submission.objects.count(), 1)

    def test_retrieve_submission(self):
        submission = Submission.objects.create(
            assignment=self.assignment,
            submitted_by=self.reviewee,
            description='Initial submission'
        )

        self.client.force_authenticate(user=self.reviewee)
        url = reverse('reviewee-retrieve-update-submission', args=[self.assignment.id, submission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], submission.description)

    def test_update_submission(self):
        submission = Submission.objects.create(
            assignment=self.assignment,
            submitted_by=self.reviewee,
            description='Initial submission'
        )

        self.client.force_authenticate(user=self.reviewee)
        url = reverse('reviewee-retrieve-update-submission', args=[self.assignment.id, submission.id])
        data = {
            'description': 'Updated submission description'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        submission.refresh_from_db()
        self.assertEqual(submission.description, 'Updated submission description')
