from rest_framework import serializers
from ajax.serializers import JobSerializer, RacerSerializer, RaceEntrySerializer
from runs.models import Run
from dispatch.models import Message

class RunSerializer(serializers.ModelSerializer):
    job = JobSerializer()
    localized_due_time = serializers.CharField(source='localized_due_time')
    localized_ready_time = serializers.CharField(source='localized_ready_time')
    status_as_string = serializers.CharField(source='status_as_string')
    late = serializers.BooleanField(source='late')
    class Meta:
        model = Run
        fields = ('job', 'status', 'id', 'localized_due_time', 'localized_ready_time', 'status_as_string', 'late')

#TODO add message time in some kind of readable format
class MessageSerializer(serializers.ModelSerializer):
    runs = RunSerializer()
    race_entry = RaceEntrySerializer()
    message_type_as_string = serializers.CharField(source='message_type_as_string')
    message_status_as_string = serializers.CharField(source='message_status_as_string')
    class Meta:
        model = Message
        fields = ('id', 'race_entry', 'runs', 'message_type', 'message_type_as_string', 'status', 'message_status_as_string', 'message_time')