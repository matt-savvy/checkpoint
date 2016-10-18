# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Race.checkpoint_app_on'
        db.delete_column(u'races_race', 'checkpoint_app_on')


    def backwards(self, orm):
        # Adding field 'Race.checkpoint_app_on'
        db.add_column(u'races_race', 'checkpoint_app_on',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    models = {
        u'races.race': {
            'Meta': {'object_name': 'Race'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'race_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'race_start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'race_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['races']