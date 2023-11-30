# serializers.py

from rest_framework import serializers
from .models import User, VolunteerEvent, Participation, Feedback

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class VolunteerEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerEvent
        fields = '__all__'

class ParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participation
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
