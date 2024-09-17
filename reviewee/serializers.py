from rest_framework import serializers
from assignment.models import Submission, Assignment, Subtask, File


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'



class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    attachments = serializers.ListField(
        child=serializers.FileField(allow_empty_file=True, use_url=False),
        required=False
    )

    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['submitted_by', 'assignment', 'is_group_submission']

    def validate(self, attrs):
        attrs['submitted_by'] = self.context['request'].user
        attrs['assignment'] = Assignment.objects.get(pk=self.context.get('assignment_pk'))
        if attrs['assignment'].assigned_to.filter(id=attrs['submitted_by'].id).exists():
            attrs['is_group_submission'] = False
        elif attrs['assignment'].assigned_to_teams.filter(members__id=attrs['submitted_by'].id).exists():
            attrs['is_group_submission'] = True
        else:
            raise serializers.ValidationError(f"Assignment {attrs['assignment'].title} not assigned to you.")
        return attrs

    def create(self, validated_data):
        attachments = validated_data.pop('attachments', [])
        assignment = super().create(validated_data)

        for file in attachments:
            attachment = File.objects.create(file=file)
            assignment.files.add(attachment)

        return assignment
