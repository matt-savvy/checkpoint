from rest_framework import serializers

from checkpoints.models import Checkpoint
from racers.models import Racer

class CheckpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkpoint

class RacerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Racer