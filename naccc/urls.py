from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from django.contrib import admin

import home.views as home_views
import racers.views as racer_views
import checkpoints.views as checkpoint_views
import races.views as race_views
import jobs.views as job_views
import raceentries.views as entry_views
import racecontrol.views as racecontrol_views
import ajax.views as ajax_views
import streamer.views as streamer_views
import results.views as result_views
import appapi.views as app_views
import authorizedcheckpoints.views as authorized_views
import mobilecheckpoint.views as mobile_views
import runs.views as run_views
import racelogs.views as log_views
import paypal.standard.ipn.signals
import dispatch.views as dispatch_views
import company_dispatch.views as company_dispatch_views
import company_entries.views as company_entries_views

admin.autodiscover()

urlpatterns = patterns('',

    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),

    url(r'^nunya/', include(admin.site.urls)),
    url(r'^$', home_views.HomeView.as_view(), name="home-view"),
    #url(r'^$', home_views.EmailTemplate.as_view(), name="email-template"),
    #url(r'^contact/$', home_views.ContactView.as_view(), name="contact-view"),
    #url(r'^schedule/$', home_views.ScheduleView.as_view(), name="schedule"),
    #url(r'^info/$', home_views.WhatIsView.as_view(), name="info"),
    # url(r'^$', login_required(home_views.HomeView.as_view())),

    #Racer URLs
    url(r'^racers/$', login_required(racer_views.RacerListView.as_view()), name="admin"),

    url(r'^racers/numbers/$', login_required(racer_views.NumbersListView.as_view()), name="racer-numbers"),
    url(r'^racers/emails/$', login_required(racer_views.EmailListView.as_view()), name="racer-emails"),
    url(r'^racers/create/$', login_required(racer_views.RacerCreateView.as_view())),
    url(r'^racers/register/$', racer_views.RacerRegisterView.as_view(), name="register-view"),
    url(r'^racers/shirt$', racer_views.RacerUpdateShirtView.as_view(), name="shirt-view"),
    url(r'^racers/registered/$', racer_views.RacerListViewPublic.as_view(), name="already-registered-view"),
    url(r'^racers/heats/$', racer_views.RacerHeatsViewPublic.as_view(), name="heats-view"),
    url(r'^racers/heats/print/$', racer_views.RacerHeatsPrintView.as_view(), name="heats-view"),

    url(r'^racers/pay/$', racer_views.view_that_asks_for_money, name="pay-view"),
    url(r'^racers/pdtreturn/$', racer_views.RegFinished, name="pdt_return_url"),
    url(r'^racers/thanks/$', racer_views.ThankYouView.as_view(), name="thank-you"),

    #volunteer URLS
    url(r'^volunteers/$', racer_views.VolunteerListView.as_view(), name="volunteer-register-view"),
    url(r'^volunteers/details/(?P<pk>[0-9]+)/$', login_required(racer_views.VolunteerDetailView.as_view())),
    url(r'^volunteers/register/$', racer_views.VolunteerRegisterView.as_view(), name="volunteer-register-view"),
    url(r'^volunteers/pay/$', racer_views.volunteer_view_that_asks_for_money, name="volunteer-pay-view"),
    url(r'^volunteers/pdtreturn/$', racer_views.VolunteerRegFinished, name="volunteer-pdt_return_url"),
    url(r'^volunteers/thanks/$', racer_views.ThankYouView.as_view(), name="volunteer-thank-you"),
    url(r'^volunteers/emails/$', racer_views.VolunteerEmailsListView.as_view(), name="volunteer-emails"),
    url(r'^volunteers/pickup/(?P<pk>[0-9]+)/$', login_required(racer_views.VolunteerPacketPickupView.as_view())),
    #
    url(r'^paypal/', include('paypal.standard.ipn.urls')),
    url(r'^racers/update/(?P<pk>[0-9]+)/$', login_required(racer_views.RacerUpdateView.as_view())),
    url(r'^racers/pickup/(?P<pk>[0-9]+)/$', login_required(racer_views.RacerPacketPickupView.as_view())),
    url(r'^racers/details/(?P<pk>[0-9]+)/$', login_required(racer_views.RacerDetailView.as_view())),
    url(r'^racers/delete/(?P<pk>[0-9]+)/$', login_required(racer_views.RacerDeleteView.as_view())),
    url(r'^racers/sessions/', login_required(racer_views.SessionListView.as_view())),
    #Checkpoint URLs
    url(r'^checkpoints/$', login_required(checkpoint_views.CheckpointListView.as_view())),
    url(r'^checkpoints/create/$', login_required(checkpoint_views.CheckpointCreateView.as_view())),
    url(r'^checkpoints/update/(?P<pk>[0-9]+)/$', login_required(checkpoint_views.CheckpointUpdateView.as_view())),
    url(r'^checkpoints/details/(?P<pk>[0-9]+)/$', login_required(checkpoint_views.CheckpointDetailView.as_view())),
    url(r'^checkpoints/delete/(?P<pk>[0-9]+)/$', login_required(checkpoint_views.CheckpointDeleteView.as_view())),
    #Race URLs
    url(r'^races/$', login_required(race_views.RaceListView.as_view())),
    url(r'^races/create/$', login_required(race_views.RaceCreateView.as_view())),
    url(r'^races/update/(?P<pk>[0-9]+)/$', login_required(race_views.RaceUpdateView.as_view())),
    url(r'^races/details/(?P<pk>[0-9]+)/$', login_required(race_views.RaceDetailView.as_view())),
    url(r'^races/delete/(?P<pk>[0-9]+)/$', login_required(race_views.RaceDeleteView.as_view())),

    url(r'^races/manifests/$', login_required(race_views.ManifestListView.as_view())),
    url(r'^races/manifests/create/$', login_required(race_views.ManifestCreateView.as_view())),
    url(r'^races/manifests/update/(?P<pk>[0-9]+)/$', login_required(race_views.ManifestUpdateView.as_view())),
    url(r'^races/manifests/details/(?P<pk>[0-9]+)/$', login_required(race_views.ManifestDetailView.as_view())),
    url(r'^races/manifests/delete/(?P<pk>[0-9]+)/$', login_required(race_views.ManifestDeleteView.as_view())),


    #Job URLs
    url(r'^jobs/$', login_required(job_views.JobRaceListView.as_view())),
    url(r'^jobs/race/(?P<race>[0-9]+)/$', login_required(job_views.JobListView.as_view())),
    url(r'^jobs/create/$', login_required(job_views.JobCreateView.as_view())),
    url(r'^jobs/update/(?P<pk>[0-9]+)/$', login_required(job_views.JobUpdateView.as_view())),
    url(r'^jobs/details/(?P<pk>[0-9]+)/$', login_required(job_views.JobDetailView.as_view())),
    url(r'^jobs/delete/(?P<pk>[0-9]+)/$', login_required(job_views.JobDeleteView.as_view())),
    url(r'^jobs/check/(?P<race>[0-9]+)/$', login_required(job_views.JobCheckView.as_view())),
    #Race Entries
    url(r'^raceentries/$', login_required(entry_views.RaceEntryRaceListView.as_view())),
    url(r'^raceentries/race/(?P<pk>[0-9]+)/$', login_required(entry_views.ManageRaceEntryView.as_view())),
    url(r'^raceentries/advance/(?P<pk>[0-9]+)/$', login_required(entry_views.AdvanceView.as_view())),
    url(r'^raceentries/enter/$', login_required(entry_views.EnterRacersView.as_view())),
    url(r'^raceentries/cuts/$', login_required(entry_views.CutListView.as_view())),
    #Race Control
    url(r'^racecontrol/$', login_required(racecontrol_views.RaceControlRaceListView.as_view())),

    url(r'^racecontrol/race/(?P<pk>[0-9]+)/$', login_required(racecontrol_views.RaceControlView.as_view())),
    url(r'^racecontrol/ajax/racerinfo/(?P<pk>[0-9]+)/$', login_required(racecontrol_views.RacerInfoView.as_view())),
    url(r'^racecontrol/ajax/racerdetail$', login_required(racecontrol_views.RacerDetailAjaxView.as_view())),
    url(r'^racecontrol/ajax/racing/(?P<pk>[0-9]+)/$', login_required(racecontrol_views.CurrentRacingView.as_view())),
    url(r'^racecontrol/ajax/notraced/(?P<pk>[0-9]+)/$', login_required(racecontrol_views.NotRacedView.as_view())),



    url(r'^racecontrol/ajax/start/(?P<pk>[0-9]+)/$', login_required(racecontrol_views.StartView.as_view())),
    url(r'^racecontrol/ajax/dq/(?P<pk>[0-9]+)/$', login_required(racecontrol_views.DQView.as_view())),
    url(r'^racecontrol/ajax/award/(?P<pk>[0-9]+)/$', login_required(racecontrol_views.AwardView.as_view())),
    url(r'^racecontrol/ajax/deduct/(?P<pk>[0-9]+)/$', login_required(racecontrol_views.DeductView.as_view())),
    url(r'^racecontrol/ajax/dnf/(?P<pk>[0-9]+)/$', login_required(racecontrol_views.DNFView.as_view())),
    url(r'^racecontrol/ajax/finish/(?P<pk>[0-9]+)/$', login_required(racecontrol_views.FinishView.as_view())),
    url(r'^racecontrol/ajax/runentry/(?P<pk>[0-9]+)/$', login_required(racecontrol_views.RunEntryView.as_view())),
    url(r'^racecontrol/ajax/racerrunentry/(?P<race>[0-9]+)/(?P<racer>[0-9]+)/$', login_required(racecontrol_views.RacerRunEntryView.as_view())),
    url(r'^racecontrol/ajax/standings/(?P<pk>[0-9]+)/$', login_required(racecontrol_views.StandingsView.as_view())),
    url(r'^racecontrol/ajax/racestatus/(?P<pk>[0-9]+)/$', login_required(racecontrol_views.RaceStatusView.as_view())),
    url(r'^racecontrol/ajax/massstart/(?P<pk>[0-9]+)/$', login_required(racecontrol_views.MassStartView.as_view())),
    #Dispatch
    #url(r'^dispatch/api/next_message/$', login_required(dispatch_views.NextMessage.as_view())),
    #url(r'^dispatch/api/rider_response/$', login_required(dispatch_views.RiderResponse.as_view())),
    #url(r'^dispatch/$', login_required(dispatch_views.DispatchView.as_view())),
    #url(r'^dispatch/radios/$', login_required(dispatch_views.RadioAssignView.as_view()), name="assign-radios"),
    #url(r'^dispatch/radios/api/$', login_required(dispatch_views.RadioAPIView.as_view())),
    #url(r'^dispatch/start_racer/$', login_required(dispatch_views.StartViewDispatch.as_view())),
    url(r'^dispatch/controls/$', login_required(dispatch_views.DispatchControlsView.as_view())),
    url(r'^dispatch/lookup/(?P<racer>[0-9]+)/$', login_required(dispatch_views.RacerLookupView.as_view())),
    #url(r'^dispatch/messages/(?P<race>[0-9]+)/$', login_required(dispatch_views.MessageListView.as_view())),

    ##COMPANY DISPATCH VIEWS
    url(r'^dispatch/$', login_required(company_dispatch_views.CompanyDispatchView.as_view())),
    url(r'^dispatch/scoreboard/$', login_required(company_dispatch_views.CompanyScoreboard.as_view())),
    url(r'^dispatch/scoreboard/refresh/$', login_required(ajax_views.DispatchScoreboardRefreshView.as_view())),
    url(r'^dispatch/finish/$', login_required(company_entries_views.CompanyEntryFinishView.as_view())),
    url(r'^dispatch/refresh/$', login_required(ajax_views.DispatchRefreshView.as_view())),
    url(r'^dispatch/assign/$', login_required(ajax_views.DispatchAssignView.as_view())),
    url(r'^dispatch/unassign/$', login_required(ajax_views.DispatchUnassignView.as_view())),


    #Ajax Views
    url(r'^ajax/racer/(?P<racer_number>[0-9]+)/$', login_required(ajax_views.RacerAjaxView.as_view())),
    url(r'^ajax/job/(?P<job_id>[0-9]+)/$', login_required(ajax_views.JobAjaxView.as_view())),
    url(r'^ajax/raceentry/$', login_required(ajax_views.RaceEntryAjaxView.as_view())),
    url(r'^ajax/startracer/$', login_required(ajax_views.StartRacerAjaxView.as_view())),
    url(r'^ajax/finishracer/$', login_required(ajax_views.FinishRacerAjaxView.as_view())),
    url(r'^ajax/dqracer/$', login_required(ajax_views.DQRacerAjaxView.as_view())),
    url(r'^ajax/undqracer/$', login_required(ajax_views.UnDQRacerAjaxView.as_view())),
    url(r'^ajax/dnfracer/$', login_required(ajax_views.DNFRacerAjaxView.as_view())),
    url(r'^ajax/checkjob/$', login_required(ajax_views.CheckJobAjaxView.as_view())),
    url(r'^ajax/run/$', login_required(ajax_views.RunAjaxView.as_view())),
    url(r'^ajax/deleterun/$', login_required(ajax_views.DeleteRunAjaxView.as_view())),
    url(r'^ajax/awardracer/$', login_required(ajax_views.AwardRacerAjaxView.as_view())),
    url(r'^ajax/deductracer/$', login_required(ajax_views.DeductRacerAjaxView.as_view())),
    url(r'^ajax/racernotes/$', login_required(ajax_views.UpdateRacerNotes.as_view())),
    url(r'^ajax/postresultstream/$', login_required(ajax_views.PostResultsStreamAjaxView.as_view())),
    url(r'^ajax/setracestarttime/$', login_required(ajax_views.SetRaceStartTime.as_view())),
    url(r'^ajax/setcurrentrace/$', login_required(ajax_views.SetCurrentRace.as_view())),
    url(r'^ajax/massstartracers/$', login_required(ajax_views.MassStartRacers.as_view())),
    url(r'^ajax/massstartcompanies/$', login_required(ajax_views.MassStartCompanies.as_view())),

    url(r'^ajax/racerpaid/$', login_required(ajax_views.MarkAsPaidRacerAjaxView.as_view())),
    #runs views
    url(r'^commission/(?P<race>[0-9]+)/(?P<racer>[0-9]+)/$', login_required(run_views.CommissionView.as_view())),
    url(r'^races/runs/(?P<race>[0-9]+)/$', login_required(run_views.RunListView.as_view())),
    #log views
    url(r'^events/(?P<minute>[0-9]+)/$', log_views.RaceEventListView.as_view()),
    url(r'^logs/(?P<racer>[0-9]+)/$', log_views.RaceLogListView.as_view()),
    url(r'^playback/$', log_views.PlaybackView.as_view()),
    #Results Streaming Views
    url(r'^streamer/$', login_required(streamer_views.StreamerView.as_view())),
    #Results View
    url(r'^results/$', login_required(result_views.ResultsGenerationView.as_view())),
    #users View
    #Authroized Checkpoints View
    url(r'^authorizedcheckpoints/$', login_required(authorized_views.AuthorizedCheckpointsList.as_view())),
    url(r'^authorizedcheckpoints/update/(?P<pk>[0-9]+)/$', login_required(authorized_views.UpdateAuthorizedCheckpoints.as_view())),
    #Checkpoint Control
    url(r'^mobilecheckpoint/$', login_required(mobile_views.WorkerAuthorizedCheckpointView.as_view())),
    url(r'^mobilecheckpoint/legacy/(?P<pk>[0-9]+)/$', login_required(mobile_views.MobileCheckpointControlLegacyView.as_view()), name="mobile_checkpoint-legacy"),
    url(r'^mobilecheckpoint/(?P<pk>[0-9]+)/$', login_required(mobile_views.MobileCheckpointControlView.as_view()), name="mobile_checkpoint"),
    #App API
    url(r'^oauth2/', include('provider.oauth2.urls', namespace = 'oauth2')),
    url(r'^api/v1/checkpoints/$', app_views.AvailableCheckpointsView.as_view()),
    url(r'^api/v1/pick/$', app_views.PickView.as_view()),
    url(r'^api/v1/drop/$', app_views.DropView.as_view()),
    url(r'^api/v1/ping/$', app_views.PingView.as_view()),
    url(r'^api/v1/id/$', app_views.CheckpointIdentificationView.as_view()),
    url(r'^api/v1/racer/$', app_views.RacerCheckpointView.as_view()),
    url(r'^api/v1/racer/(?P<racer_number>[0-9]+)/$', app_views.RacerDetailView.as_view()),
)
