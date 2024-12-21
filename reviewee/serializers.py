from rest_framework import serializers
from assignment.models import (
    Submission,
    Assignment,
    Subtask,
    File,
    Review
)
from assignment.serializers import (
    FileSerializer,
    RevieweeSerializer
)


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = '__all__'


class AssignmentSerializer(serializers.ModelSerializer):
    subtasks = SubtaskSerializer(many=True, read_only=True)
    files = FileSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = '__all__'

    def get_status(self, obj):
        submissions = Submission.objects.filter(assignment=obj)

        if not submissions.exists():
            return 'Pending'

        # Find the latest submission's review status
        latest_submission = submissions.order_by('-created_at').first()
        latest_review = latest_submission.reviews.order_by('-created_at').first()

        if latest_review:
            return latest_review.status
        else:
            return 'Pending'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, required=False)
    reviews = ReviewSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()
    submitted_by = RevieweeSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['submitted_by', 'assignment', 'is_group_submission']

    def get_status(self, obj):
        latest_review = obj.reviews.order_by('-created_at').first()
        return latest_review.status if latest_review else 'Pending'

    def validate(self, attrs):
        attrs['submitted_by'] = self.context['request'].user
        attrs['assignment'] = Assignment.objects.get(pk=self.context['view'].kwargs.get('assignment_pk'))
        if attrs['assignment'].assigned_to.filter(id=attrs['submitted_by'].id).exists():
            attrs['is_group_submission'] = False
        elif attrs['assignment'].assigned_to_teams.filter(members__id=attrs['submitted_by'].id).exists():
            attrs['is_group_submission'] = True
        else:
            raise serializers.ValidationError(f"Assignment {attrs['assignment'].title} not assigned to you.")
        return attrs

    def create(self, validated_data):
        files = self.context['request'].FILES.getlist('files', [])
        assignment = super().create(validated_data)

        for file in files:
            attachment = File.objects.create(file=file)
            assignment.files.add(attachment)

        return assignment
