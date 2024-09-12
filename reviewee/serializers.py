from rest_framework.serializers import ModelSerializer
from assignment.models import Submission, Assignment


class AssignmentSerializer(ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'


class SubmissionSerializer(ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['subtask', 'submitted_by', 'status', 'reviewed_by', 'feedback']

    def create(self, validated_data):
        validated_data['submitted_by'] = self.context['request'].user
        validated_data['subtask'] = self.context['subtask']
        validated_data['status'] = "Pending Review"
        return super().create(validated_data)
