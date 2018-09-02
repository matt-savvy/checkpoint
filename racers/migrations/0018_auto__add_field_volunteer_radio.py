# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Volunteer.radio'
        db.add_column(u'racers_volunteer', 'radio',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Volunteer.radio'
        db.delete_column(u'racers_volunteer', 'radio')


    models = {
        u'racers.racer': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'Racer'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '50', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'nick_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paypal_tx': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'racer_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'shirt_size': ('django.db.models.fields.CharField', [], {'default': "'M'", 'max_length': '2'}),
            'team': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'racers.volunteer': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'Volunteer'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '50', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'fixed_gear': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'packet_picked_up': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paypal_tx': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'radio': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'shirt_size': ('django.db.models.fields.CharField', [], {'default': "'M'", 'max_length': '2'})
        }
    }

    complete_apps = ['racers']