# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'RaceEntry.final_time'
        db.alter_column(u'raceentries_raceentry', 'final_time', self.gf('django.db.models.fields.TimeField')(null=True))

        # Changing field 'RaceEntry.start_time'
        db.alter_column(u'raceentries_raceentry', 'start_time', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'RaceEntry.end_time'
        db.alter_column(u'raceentries_raceentry', 'end_time', self.gf('django.db.models.fields.DateTimeField')(null=True))

    def backwards(self, orm):

        # Changing field 'RaceEntry.final_time'
        db.alter_column(u'raceentries_raceentry', 'final_time', self.gf('django.db.models.fields.TimeField')(default=datetime.datetime(2014, 5, 12, 0, 0)))

        # Changing field 'RaceEntry.start_time'
        db.alter_column(u'raceentries_raceentry', 'start_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 5, 12, 0, 0)))

        # Changing field 'RaceEntry.end_time'
        db.alter_column(u'raceentries_raceentry', 'end_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 5, 12, 0, 0)))

    models = {
        u'raceentries.raceentry': {
            'Meta': {'unique_together': "(('racer', 'race'),)", 'object_name': 'RaceEntry'},
            'deductions': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            'dq_reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'dq_time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'entry_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'entry_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'final_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'grand_total': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points_earned': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['races.Race']"}),
            'racer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['racers.Racer']"}),
            'scratch_pad': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'racers.racer': {
            'Meta': {'object_name': 'Racer'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'nick_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'racer_number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'races.race': {
            'Meta': {'object_name': 'Race'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mass_start': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'race_date': ('django.db.models.fields.DateField', [], {}),
            'race_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['raceentries']