# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Race.time_limit'
        db.delete_column(u'races_race', 'time_limit')

        # Deleting field 'Race.mass_start'
        db.delete_column(u'races_race', 'mass_start')

        # Deleting field 'Race.race_date'
        db.delete_column(u'races_race', 'race_date')

        # Adding field 'Race.race_type'
        db.add_column(u'races_race', 'race_type',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Race.time_limit'
        db.add_column(u'races_race', 'time_limit',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Race.mass_start'
        db.add_column(u'races_race', 'mass_start',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Race.race_date'
        db.add_column(u'races_race', 'race_date',
                      self.gf('django.db.models.fields.DateField')(default=0),
                      keep_default=False)

        # Deleting field 'Race.race_type'
        db.delete_column(u'races_race', 'race_type')


    models = {
        u'races.race': {
            'Meta': {'object_name': 'Race'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'race_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'race_type': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        }
    }

    complete_apps = ['races']