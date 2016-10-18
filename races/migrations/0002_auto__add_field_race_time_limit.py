# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Race.time_limit'
        db.add_column(u'races_race', 'time_limit',
                      self.gf('django.db.models.fields.IntegerField')(default=60),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Race.time_limit'
        db.delete_column(u'races_race', 'time_limit')


    models = {
        u'races.race': {
            'Meta': {'object_name': 'Race'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mass_start': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'race_date': ('django.db.models.fields.DateField', [], {}),
            'race_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['races']