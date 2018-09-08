from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Message
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import OAuth2Authentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from dispatch.serializers import MessageSerializer, RunSerializer
from racecontrol.models import RaceControl
from .util import get_next_message


class NextMessage(APIView):
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        current_race = RaceControl.shared_instance().current_race
        
        next_message = get_next_message(current_race)
        
        if next_message:
            return Response(MessageSerializer(next_message).data, status=status.HTTP_200_OK)
            #return Response({'error' : False, 'error_title' : None, 'error_description' : None}, status=status.HTTP_200_OK)
            
        return
        
class MessageListView(ListView):
    model = Message
    context_object_name = 'messages'
    
    def get_queryset(self):
        return Message.objects.filter(race__pk=self.kwargs['race'])