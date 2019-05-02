from rest_framework import serializers
from racers.models import Racer, Volunteer
from raceentries.models import RaceEntry
from jobs.models import Job
from checkpoints.models import Checkpoint
from runs.models import Run
from companies.models import Company
from company_entries.models import CompanyEntry

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('name', 'id')

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
    company = CompanySerializer()
    class Meta:
        model = Racer
        fields = ('racer_number', 'first_name', 'last_name', 'nick_name', 'city', 'gender', 'category', 'display_name', 'category_as_string', 'radio_number', 'contact_info', 'company')

class RaceEntrySerializer(serializers.ModelSerializer):
    entry_status_as_string = serializers.CharField(source='entry_status_as_string')
    localized_start_time = serializers.CharField(source='localized_start_time')
    current_score = serializers.CharField(source='calculate_current_score')
    racer = RacerSerializer()
    class Meta:
        model = RaceEntry
        depth = 2
        fields = ('entry_status_as_string', 'localized_start_time', 'current_score', 'racer', 'id')

class CheckpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkpoint


class JobSerializer(serializers.ModelSerializer):
    pick_checkpoint = CheckpointSerializer()
    drop_checkpoint = CheckpointSerializer()
    service = serializers.CharField(source='service')
    points = serializers.CharField()

    class Meta:
        model = Job
        depth = 2
        fields = ('pick_checkpoint', 'drop_checkpoint', 'service', 'points', 'minutes_due_after_start')

class RunSerializer(serializers.ModelSerializer):
    job = JobSerializer()
    race_entry = RaceEntrySerializer()
    status_as_string = serializers.CharField(source='status_as_string')
    number_of_open_jobs = serializers.CharField(source='number_of_open_jobs')
    determination_as_string = serializers.CharField(source='determination_as_string')

    class Meta:
        model = Run
        fields = ('id', 'race_entry', 'job', 'status_as_string', 'utc_time_ready', 'utc_time_due', 'utc_time_picked', 'utc_time_dropped', 'determination_as_string')


class CompanyEntrySerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    #race = RaceSerializer()
    race_entries = RaceEntrySerializer(source='get_race_entries', many=True)
    runs = RunSerializer(source='get_runs', many=True)

    class Meta:
        model = CompanyEntry
        fields = ('company', 'id', 'race_entries', 'runs')
