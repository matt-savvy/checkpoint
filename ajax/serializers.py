from rest_framework import serializers
from racers.models import Racer, Volunteer
from raceentries.models import RaceEntry
from jobs.models import Job
from checkpoints.models import Checkpoint
from runs.models import Run


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Racer
        fields = ('racer_number', 'first_name', 'last_name', 'nick_name', 'email', 'city', 'gender', 'category', 'shirt_size', 'paid', 'team', 'company')
    
    def create(self, validated_data):
            return Racer(**validated_data)




class VolunteerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volunteer
        fields = ('first_name', 'last_name', 'email', 'phone', 'city', 'shirt_size', 'paid')
    
    def create(self, validated_data):
            return Volunteer(**validated_data)

class RacerSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='display_name')
    category_as_string = serializers.CharField(source='category_as_string')
    class Meta:
        model = Racer
        fields = ('racer_number', 'first_name', 'last_name', 'nick_name', 'city', 'gender', 'category', 'display_name', 'category_as_string', 'radio_number', 'contact_info')

class RaceEntrySerializer(serializers.ModelSerializer):
    entry_status_as_string = serializers.CharField(source='entry_status_as_string')
    racer = RacerSerializer()
    class Meta:
        model = RaceEntry
        depth = 2

class CheckpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkpoint

class JobSerializer(serializers.ModelSerializer):
    pick_checkpoint = CheckpointSerializer()
    drop_checkpoint = CheckpointSerializer()
    service = serializers.CharField(source='service')
    
    class Meta:
        model = Job
        depth = 2
        fields = ('pick_checkpoint', 'drop_checkpoint', 'service', 'minutes_due_after_start', 'manifest')
        
class RunSerializer(serializers.ModelSerializer):
    job = JobSerializer()
    status_as_string = serializers.CharField(source='status_as_string')
    class Meta:
        model = Run
        fields = ('id', 'job', 'status_as_string')