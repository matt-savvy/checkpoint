# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Race.race_start_time'
        db.add_column(u'races_race', 'race_start_time',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Race.checkpoint_app_on'
        db.add_column(u'races_race', 'checkpoint_app_on',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Race.race_start_time'
        db.delete_column(u'races_race', 'race_start_time')

        # Deleting field 'Race.checkpoint_app_on'
        db.delete_column(u'races_race', 'checkpoint_app_on')


    models = {
        u'races.race': {
            'Meta': {'object_name': 'Race'},
            'checkpoint_app_on': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'race_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'race_start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'race_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['races']