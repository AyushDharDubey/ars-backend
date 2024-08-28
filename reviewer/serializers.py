from rest_framework import serializers
from assignment.models import (
    Assignment,
    Subtask,
    Team,
)
from datetime import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model

User = get_user_model()

class CreateTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['created_by', ]
    
    def validate(self, attrs):
        self.user = self.context['view'].request.user
        if attrs.get('reviewers') is None:
            attrs['reviewers'] = []
        if not self.user in attrs['reviewers']:
            attrs['reviewers'].append(self.user)
        if attrs.get('assigned_to') is None:
            attrs['assigned_to'] = []
        if attrs.get('assigned_to_teams') is None:
            attrs['assigned_to_teams'] = []
        if len(attrs['assigned_to'])==0 and len(attrs['assigned_to_teams']==0):
            raise serializers.ValidationError(
                'at least one of assigned_to or assigned_to_teams parameter is required'
            )
        return attrs
        return attrs

    def create(self, validated_data):
        validated_data['created_by'] = self.user
        return super().create(validated_data)


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        exclude = ['assignment']

    def create(self, validated_data):
        validated_data['assignment'] = self.context.get('assignment_pk')
        return super().create(validated_data)