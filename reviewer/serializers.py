from rest_framework import serializers
from assignment.models import (
    Assignment,
    Subtask,
    Team,
    Review,
    Submission,
    File
)
from assignment.serializers import (
    FileSerializer
)
from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

class RevieweeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        read_only_fields = ['id', 'username']
        fields = ['id', 'username']


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


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = '__all__'


class AssignmentSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, required=False)
    subtasks = SubtaskSerializer(many=True, read_only=True)
    assigned_to = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.filter(groups__name="Reviewee"),
        required=False
    )
    assigned_to_teams = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Team.objects.all(), required=False
    )
    reviewers = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.filter(groups__name="Reviewer"),
        required=False
    )
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())


    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, attrs):
        self.user = self.context['view'].request.user

        if not self.partial:
            if not self.user in attrs.get('reviewers', []):
                attrs['reviewers'].append(self.user)
            if not attrs.get('assigned_to') and not attrs.get('assigned_to_teams'):
                raise serializers.ValidationError(
                    'Assignment must be assigned to either individuals or teams.'
                )
        return attrs
    
    def validate_due_date(self, due_date):
        if due_date <= timezone.now():
            raise serializers.ValidationError("Due date must be a future date.")
        return due_date

    def create(self, validated_data):
        files = self.context['request'].FILES.getlist('files', [])
        subtasks_data = validated_data.pop("subtasks", [])
        assignment = super().create(validated_data)
        print(assignment.assigned_to_teams)

        for file in files:
            uploaded_file = File.objects.create(file=file)
            assignment.files.add(uploaded_file)

        for subtask_data in subtasks_data:
            Subtask.objects.create(assignment=assignment, **subtask_data)

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
    status = serializers.SerializerMethodField()
    submitted_by = RevieweeSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = "__all__"

    def get_status(self, obj):
        latest_review = obj.reviews.order_by('-created_at').first()
        return latest_review.status if latest_review else 'Pending'