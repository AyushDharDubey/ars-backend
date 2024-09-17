from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import PasswordField
from .utils import send_account_activation
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    user = None
    username = serializers.CharField()
    password = PasswordField()

    def validate(self, data):
        request = self.context.get('request')

        user = authenticate(
            request,
            username=data.get('username'),
            password=data.get('password')
        )
        if user is not None:
            self.user = user
        else:
            raise serializers.ValidationError('Invalid credentials provided.')

        return data


class ResetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate_username(self, username):
        try:
            self.user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError('User doesn\'t exist')
        return username

    def validate_token(self, token):
        if default_token_generator.check_token(self.user, token):
            return token
        else:
            raise serializers.ValidationError('Invalid token')


class AccountActivateSerializer(serializers.Serializer):
    username = serializers.CharField()
    token = serializers.CharField(allow_blank=True, required=False)
    otp = serializers.CharField(allow_blank=True, required=False)

    def validate_username(self, username):
        try:
            self.user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError('User doesn\'t exist')
        return username

    def validate(self, data):
        request = self.context.get('request')

        if data.get('username'):
            user = User.objects.get(username=data.get('username'))
        elif request.user.is_authenticated:
            user = request.user
        else:
            raise serializers.ValidationError('User doesn\'t exist')
        
        if (user.otp == data.get('otp') or user.email_verification_token == data.get('token')):
            return data
        elif data.get('otp'):
            raise serializers.ValidationError('Incorrect OTP')
        elif data.get('token'):
            raise serializers.ValidationError('Incorrect token')
        else:
            raise serializers.ValidationError('Token or OTP not found')


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        send_account_activation(user)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()

    def validate_current_password(self, current_password):
        self.user = self.context.get('request').user
        auth = authenticate(username=self.user.username, password=current_password)
        if not auth:
            raise serializers.ValidationError('Wrong password')
        return current_password
