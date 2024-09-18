from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
        self.user.is_active = True
        self.user.save()
        self.group = Group.objects.create(name="Reviewee")
    
    def test_signup(self):
        url = reverse('signup')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'Reviewee'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_signup_invalid_role(self):
        url = reverse('signup')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'InvalidRole'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid role', response.data['errors']['non_field_errors'])

    def test_login(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        url = reverse('login')
        data = {
            'username': 'wronguser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid credentials provided.', response.data['errors']['non_field_errors'])

    def test_logout(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.force_authenticate(user=self.user)
        url = reverse('logout')
        data = {
            'refresh_token': str(refresh)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_account_activation_email_sent(self):
        self.user.is_active = False
        self.user.save()

        self.client.force_authenticate(user=self.user)
        url = reverse('activate-account')

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'Email sent successfully')
        cache.clear()

    def test_account_activation_already_active(self):
        self.user.is_active = True
        self.user.save()

        self.client.force_authenticate(user=self.user)
        url = reverse('activate-account')

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email already verified', response.data['error'])

    def test_account_activation_invalid_otp(self):
        self.user.is_active = False
        self.user.otp = '654321'
        self.user.email_verification_token = 'not null'
        self.user.save()

        self.client.force_authenticate(user=self.user)
        url = reverse('activate-account')
        data = {
            'username': self.user.username,
            'otp': '123456'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Incorrect OTP', response.data['errors']['non_field_errors'])

    def test_account_activation_with_valid_otp(self):
        self.user.is_active = False
        self.user.otp = '123456'
        self.user.save()

        self.client.force_authenticate(user=self.user)
        url = reverse('activate-account')
        data = {
            'username': self.user.username,
            'otp': '123456'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


    def test_reset_password(self):
        url = reverse('reset-password')
        data = {
            'username': 'testuser'
        }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cache.clear()

    def test_reset_password_invalid_username(self):
        url = reverse('reset-password')
        data = {
            'username': 'wronguser'
        }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('The username provided is incorrect', response.data)

    def test_change_password(self):
        self.user.is_active = True
        self.client.force_authenticate(user=self.user)
        url = reverse('change-password')
        data = {
            'current_password': 'password123',
            'new_password': 'newpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_invalid(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('change-password')
        data = {
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Wrong password', response.data['errors']['current_password'])
