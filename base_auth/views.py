from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .serializers import SignupSerializer, LoginSerializer, ResetPasswordSerializer, AccountActivateSerializer, ChangePasswordSerializer
from .models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .utils import send_password_reset, send_account_activation
from rest_framework.generics import GenericAPIView


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
                'refresh': str(refresh_token),
                'access': str(access_token)
            }
            return Response(content, status=status.HTTP_201_CREATED)
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
        if request.data.get('role') in ["Reviewee", "Reviewer"]:
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
                'refresh': str(refresh_token),
                'access': str(access_token)
            }
            return Response(content, status=status.HTTP_201_CREATED)
        else:
            return Response(
                data={
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class AccountActivateView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AccountActivateSerializer


    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_active:
            if send_account_activation(user):
                return Response('Email sent successfully', status=status.HTTP_200_OK)
            else:
                return Response({'error': 'try after some time'}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Email already verified'}, status.HTTP_400_BAD_REQUEST)



    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.user
            user.is_active = True
            user.otp = None
            user.email_verification_token = None
            user.save()
            return Response(
                data={
                    'status': 'Account activated successfully'
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
