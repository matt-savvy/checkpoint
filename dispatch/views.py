from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.authentication import OAuth2Authentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from nacccusers.auth import AuthorizedRaceOfficalMixin
from .models import Message
from runs.models import Run
from dispatch.serializers import MessageSerializer, RunSerializer
from racecontrol.models import RaceControl
from .util import get_next_message
from raceentries.models import RaceEntry
from ajax.serializers import RaceEntrySerializer


class NextMessage(APIView):
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        current_race = RaceControl.shared_instance().current_race
        error = None
        next_message = get_next_message(current_race)
        
        try:
            error = next_message[1]
            next_message = next_message[0]
        except:
            error = None
            next_message
        
        if next_message:
            #return Response(MessageSerializer(next_message).data, status=status.HTTP_200_OK)
            return Response({'message': MessageSerializer(next_message).data, 'error_description' : error}, status=status.HTTP_200_OK)
            #return Response({'error' : False, 'error_title' : None, 'error_description' : None}, status=status.HTTP_200_OK)
            
        return

class RiderResponse(APIView):
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        current_race = RaceControl.shared_instance().current_race
        message_pk = self.request.DATA.get('message')
        message = Message.objects.get(pk=message_pk)
        action = self.request.DATA.get('action')
        
        if action == "CONFIRM":
            message = message.confirm()
        elif action == "SNOOZE":
            message = message.snooze()
        elif action == "UNDO":
            message.status = Message.MESSAGE_STATUS_DISPATCHING
            message.confirmed_time = None
            message.save()
            if message.message_type == Message.MESSAGE_TYPE_DISPATCH:
                for run in message.runs.all():
                    run.run_status = Run.RUN_STATUS_DISPATCHING
                    run.save()
            #TODO log this undo
        return Response(MessageSerializer(message).data, status=status.HTTP_200_OK)
        
class MessageListView(AuthorizedRaceOfficalMixin, ListView):
    model = Message
    
    def get_queryset(self):
        return Message.objects.filter(race_entry__race__pk=self.kwargs['race'])
        
class DispatchView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = "dispatch.html"
    
    method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super(DispatchView, self).dispatch(request, *args, **kwargs)
        
    def render_to_response(self, context, **response_kwargs):
        response = super(DispatchView, self).render_to_response(context, **response_kwargs)
        current_race = RaceControl.shared_instance().current_race
        response.set_cookie('raceID', current_race.pk)
        return response

class StartViewDispatch(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = "start_racer_react.html"
    
    method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super(StartViewDispatch, self).dispatch(request, *args, **kwargs)
        
    def render_to_response(self, context, **response_kwargs):
        response = super(StartViewDispatch, self).render_to_response(context, **response_kwargs)
        current_race = RaceControl.shared_instance().current_race
        response.set_cookie('raceID', current_race.pk)
        return response

class RacerLookupView(APIView):
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        current_race = RaceControl.shared_instance().current_race
        
        race_entry = RaceEntry.objects.filter(race=current_race).filter(racer__racer_number=kwargs['racer']).first()

        if race_entry:
            return Response(RaceEntrySerializer(race_entry).data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    