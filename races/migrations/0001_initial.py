# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Race'
        db.create_table(u'races_race', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('race_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('race_date', self.gf('django.db.models.fields.DateField')()),
            ('mass_start', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'races', ['Race'])


    def backwards(self, orm):
        # Deleting model 'Race'
        db.delete_table(u'races_race')


    models = {
        u'races.race': {
            'Meta': {'object_name': 'Race'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mass_start': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'race_date': ('django.db.models.fields.DateField', [], {}),
            'race_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['races']