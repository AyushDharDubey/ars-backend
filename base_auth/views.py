from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    OauthChanneliSerializer,
    ProfileSerializer,
)
from .models import User
from rest_framework.permissions import IsAuthenticated
from .utils import send_password_reset, send_account_activation
from rest_framework.generics import GenericAPIView, RetrieveAPIView


class ProfileView(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(
                data={
                    'errors': {
                    'non_field_errors': [
                        'You are already logged in.',
                    ],
                },
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.user

            refresh_token = RefreshToken.for_user(user)
            access_token = AccessToken.for_user(user)
            content = {
                'refresh_token': str(refresh_token),
                'access_token': str(access_token),
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
            return Response(content, status=status.HTTP_200_OK)
        else:
            return Response(
                data={
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        refresh_token = request.data["refresh_token"]
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response(
            data={
                'status': 'Successfully logged out',
            },
            status=status.HTTP_205_RESET_CONTENT
        )


class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = []

    def get(self, request, *args, **kwargs):
        username = request.GET.get('username', None)

        if username is None:
            return Response(
                data="Please provide the username",
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                data="The username provided is incorrect",
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if send_password_reset(user):
            return Response(
                data='Email sent successfully',
                status=status.HTTP_200_OK,
            )
        else:
            return Response(data='try after some time', status=status.HTTP_400_BAD_REQUEST)


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.user
            user.set_password(serializer.validated_data.get('new_password'))
            user.save()
            return Response(
                data={
                    'status': 'Successfully reset password'
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                data={
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ChangePasswordView(GenericAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.user.set_password(request.data['new_password'])
            serializer.user.save()
            return Response(
                data={
                    'status': 'Successfully reset password'
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                data = {
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class SignupAPIView(GenericAPIView):
    serializer_class = SignupSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(
                data={
                    'errors': {
                    'non_field_errors': [
                        'You are already logged in.',
                    ],
                },
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.data.get('role') in ["Reviewee", "Reviewer", "Admin"]:
            group = Group.objects.get(name = request.data['role'])
        else:
            return Response(
                data={
                    'errors': {
                    'non_field_errors': [
                        'Invalid role',
                    ],
                },
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.groups.add(group)
            user.save()
            refresh_token = RefreshToken.for_user(user)
            access_token = AccessToken.for_user(user)
            content={
                'refresh_token': str(refresh_token),
                'access_token': str(access_token)
            }
            return Response(content, status=status.HTTP_201_CREATED)
        else:
            return Response(
                data={
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class OauthChanneliView(GenericAPIView):
    permission_classes = []
    serializer_class = OauthChanneliSerializer

    def get(self, request):
        serializer = self.get_serializer(data=request.GET)
        if not serializer.is_valid():
            return Response(
                data={
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        user_info = serializer.validated_data['user_info']
        role = serializer.validated_data['state']
        username = user_info.get('username')
        email = user_info.get('contactInformation').get('emailAddress')

        user, created = User.objects.update_or_create(
            username=username,
            defaults={
                'first_name': user_info.get('person').get('fullName'),
                'email': email,
                'registration_method': 'channel i',
                'is_active': True,
            }
        )

        if not created:
            if User.objects.filter(email=email).exclude(username=username).exists():
                return Response(
                    data={'errors': 'Another user with this email already exists.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        group = Group.objects.get(name=role)
        user.groups.add(group)

        refresh_token = RefreshToken.for_user(user)
        access_token = AccessToken.for_user(user)
        return Response(
            data={
                'access_token': str(access_token),
                'refresh_token': str(refresh_token)
            },
            status=status.HTTP_200_OK
        )
