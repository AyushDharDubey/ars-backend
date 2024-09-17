from rest_framework import serializers
from assignment.models import (
    Assignment,
    Subtask,
    Team,
    Review,
    Submission,
    File
)
from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
    
    def validate_members(self, members):
        reviewee_group = Group.objects.get(name='Reviewee')
        
        for member in members:
            if not reviewee_group in member.groups.all():
                raise serializers.ValidationError(f"User {member.username} must be a Reviewee.")
        
        return members


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        exclude = ['assignment']

    def create(self, validated_data):
        validated_data['assignment'] = Assignment.objects.get(
            pk=self.context['view'].kwargs.get('assignment_pk')
        )
        return super().create(validated_data)


class AssignmentSerializer(serializers.ModelSerializer):
    attachments = serializers.ListField(
        child=serializers.FileField(allow_empty_file=True, use_url=False),
        required=False
    )
    subtasks = SubtaskSerializer(many=True, read_only=True)
    files = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        self.user = self.context['view'].request.user
        if attrs.get('reviewers') is None:
            attrs['reviewers'] = []
        if not self.user in attrs['reviewers']:
            attrs['reviewers'].append(self.user)
        if not self.partial:
            if attrs.get('assigned_to') is None:
                attrs['assigned_to'] = []
            if attrs.get('assigned_to_teams') is None:
                attrs['assigned_to_teams'] = []
            if len(attrs['assigned_to'])==0 and len(attrs['assigned_to_teams'])==0:
                raise serializers.ValidationError(
                    'Assignment must be assigned to either individuals or teams.'
                )
        return attrs
    
    def validate_assigned_to(self, users):
        reviewee_group = Group.objects.get(name='Reviewee')
        for user in users:
            if not reviewee_group in user.groups.all():
                raise serializers.ValidationError(f"User {user.username} must be a Reviewee.")
        return users
    
    def validate_due_date(self, due_date):
        if due_date <= timezone.now():
            raise serializers.ValidationError("Due date must be a future date.")
        return due_date
    
    def validate_reviewers(self, reviewers):
        reviewer_group = Group.objects.get(name='Reviewer')
        for user in reviewers:
            if not reviewer_group in user.groups.all():
                raise serializers.ValidationError(f"User {user.username} must be a Reviewer.")
        return reviewers
        

    def create(self, validated_data):
        attachments = validated_data.pop('attachments', [])
        validated_data['created_by'] = self.context['request'].user
        assignment = super().create(validated_data)

        for file in attachments:
            attachment = File.objects.create(file=file)
            assignment.files.add(attachment)

        return assignment


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["submission", "reviewer", "created_at", "updated_at"]

    def validate(self, attrs):
        attrs['reviewer'] = self.context['view'].request.user
        attrs['submission'] = Submission.objects.get(
            pk=self.context['view'].kwargs.get('submission_pk')
        )
        if not attrs['submission'].assignment.reviewers.filter(id=attrs['reviewer'].id).exists():
            raise serializers.ValidationError("You are not a reviewer for this assignment.")
        return attrs


class SubmissionSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Submission
        fields = "__all__"