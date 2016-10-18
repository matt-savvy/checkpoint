# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'RaceControl.racers_started'
        db.add_column(u'racecontrol_racecontrol', 'racers_started',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'RaceControl.racers_started'
        db.delete_column(u'racecontrol_racecontrol', 'racers_started')


    models = {
        u'racecontrol.racecontrol': {
            'Meta': {'object_name': 'RaceControl'},
            'current_race': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['races.Race']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'racers_started': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'races.race': {
            'Meta': {'object_name': 'Race'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'race_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'race_start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'race_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['racecontrol']