from rest_framework import serializers
from ajax.serializers import JobSerializer, RacerSerializer, RaceEntrySerializer
from runs.models import Run
from dispatch.models import Message

class RunSerializer(serializers.ModelSerializer):
    job = JobSerializer()
    class Meta:
        model = Run
        fields = ('job', 'status')
        
class MessageSerializer(serializers.ModelSerializer):
    runs = RunSerializer()
    race_entry = RaceEntrySerializer()
    message_type_as_string = serializers.CharField(source='message_type_as_string')
    class Meta:
        model = Message
        fields = ('id', 'race_entry', 'runs', 'message_type', 'message_type_as_string')