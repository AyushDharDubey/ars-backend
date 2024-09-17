from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assignment.models import Assignment, Subtask, Review, Submission, File
from django.utils import timezone
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class AssignmentTestCase(APITestCase):

    def setUp(self):
        self.reviewer_group = Group.objects.create(name='Reviewer')
        self.reviewee_group = Group.objects.create(name='Reviewee')
        
        self.reviewer = User.objects.create_user(username='reviewer', password='123', email='reviewer@gmail.com')
        self.reviewer.groups.add(self.reviewer_group)
        
        self.reviewee = User.objects.create_user(username='reviewee', password='123', email='reviewee@gmail.com')
        self.reviewee.groups.add(self.reviewee_group)

        self.assignment = Assignment.objects.create(
            title="Test Assignment",
            description="Assignment description",
            due_date=timezone.now() + timezone.timedelta(days=7),
            created_by=self.reviewer
        )
        self.assignment.reviewers.add(self.reviewer)

        self.test_file = SimpleUploadedFile(
            "test_file.pdf", b"This is a test file content", content_type="application/pdf"
        )

    def test_create_assignment(self):
        self.client.force_authenticate(user=self.reviewer)
        url = reverse('reviewer-create-assignment')
        data = {
            'title': 'New Assignment',
            'description': 'New Assignment Description',
            'due_date': timezone.now() + timezone.timedelta(days=10),
            'assigned_to': [self.reviewee.id, ],
            'attachments': [self.test_file, ]
        }
        response = self.client.post(url, data, format='multipart', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assignment.objects.count(), 2)
    
    def test_create_assignment_invalid_due_date(self):
        self.client.force_authenticate(user=self.reviewer)
        url = reverse('reviewer-create-assignment')
        data = {
            'title': 'Invalid Assignment',
            'description': 'New Assignment Description',
            'due_date': timezone.now() - timezone.timedelta(days=10),
            'assigned_to': [self.reviewee.id, ],
        }
        response = self.client.post(url, data, format='multipart', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Assignment.objects.count(), 1)
    
    def test_create_assignment_assigned_to_non_reviewee(self):
        self.client.force_authenticate(user=self.reviewer)
        url = reverse('reviewer-create-assignment')
        data = {
            'title': 'Invalid Assignment',
            'description': 'Assignment Description',
            'due_date': timezone.now() + timezone.timedelta(days=10),
            'assigned_to': [self.reviewer.id, ],
        }
        response = self.client.post(url, data, format='multipart', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Assignment.objects.count(), 1)

    def test_list_assignments(self):
        self.client.force_authenticate(user=self.reviewer)
        url = reverse('reviewer-list-assignments')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_assignment(self):
        self.client.force_authenticate(user=self.reviewer)
        url = reverse('reviewer-retrieve-update-assignment', args=[self.assignment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.assignment.title)

    def test_update_assignment(self):
        self.client.force_authenticate(user=self.reviewer)
        url = reverse('reviewer-retrieve-update-assignment', args=[self.assignment.id])
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data, format='json')
        self.assignment.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.assignment.title, 'Updated Title')


class SubtaskTestCase(APITestCase):

    def setUp(self):
        self.reviewer = User.objects.create_user(username='reviewer', password='123')
        self.reviewer_group = Group.objects.create(name='Reviewer')
        self.reviewer.groups.add(self.reviewer_group)
        
        self.assignment = Assignment.objects.create(
            title="Test Assignment",
            description="Assignment description",
            due_date=timezone.now() + timezone.timedelta(days=7),
            created_by=self.reviewer
        )
        self.assignment.reviewers.add(self.reviewer)

    def test_create_subtask(self):
        self.client.force_authenticate(user=self.reviewer)
        url = reverse('reviewer-create-subtask', args=[self.assignment.id])
        data = {
            'title': 'New Subtask',
            'description': 'Subtask description'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subtask.objects.count(), 1)

    def test_retrieve_subtask(self):
        self.client.force_authenticate(user=self.reviewer)
        subtask = Subtask.objects.create(
            assignment=self.assignment,
            title='Test Subtask',
            description='Subtask description'
        )
        url = reverse('reviewer-retrieve-update-subtask', args=[self.assignment.id, subtask.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], subtask.title)


class ReviewTestCase(APITestCase):

    def setUp(self):
        self.reviewer = User.objects.create_user(username='reviewer', password='123', email='reviewee@gmail.com')
        self.reviewee = User.objects.create_user(username='reviewee', password='123', email='reviewer@gmail.com')

        self.reviewer_group = Group.objects.create(name='Reviewer')
        self.reviewee_group = Group.objects.create(name='Reviewee')

        self.reviewer.groups.add(self.reviewer_group)
        self.reviewee.groups.add(self.reviewee_group)
        
        self.assignment = Assignment.objects.create(
            title="Test Assignment",
            description="Assignment description",
            due_date=timezone.now() + timezone.timedelta(days=7),
            created_by=self.reviewer
        )
        self.assignment.reviewers.add(self.reviewer)

        self.submission = Submission.objects.create(
            assignment=self.assignment,
            submitted_by=self.reviewee
        )

    def test_create_review(self):
        self.client.force_authenticate(user=self.reviewer)
        url = reverse('reviewer-create-review', args=[self.submission.id])
        data = {
            'comments': 'Good work',
            'status': 'Approved'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().status, 'Approved')

    def test_retrieve_review(self):
        self.client.force_authenticate(user=self.reviewer)
        review = Review.objects.create(
            submission=self.submission,
            reviewer=self.reviewer,
            comments='Great work',
            status='Approved'
        )
        url = reverse('reviewer-retrieve-update-review', args=[self.submission.id, review.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comments'], review.comments)
