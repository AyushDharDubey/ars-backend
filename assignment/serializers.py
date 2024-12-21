from rest_framework import serializers
from .models import (
    Message,
    File,
    Team
)
from django.contrib.auth import get_user_model

User = get_user_model()


from rest_framework import serializers

class MessageSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = ["user", "content", "created_at"]



class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'


class RevieweeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        read_only_fields = ['id', 'username']
        fields = ['id', 'username']


class ReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        read_only_fields = ['id', 'username']
        fields = ['id', 'username']