# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'RaceEntry.final_time'
        db.add_column(u'raceentries_raceentry', 'final_time',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'RaceEntry.final_time'
        db.delete_column(u'raceentries_raceentry', 'final_time')


    models = {
        u'raceentries.raceentry': {
            'Meta': {'unique_together': "(('racer', 'race'),)", 'object_name': 'RaceEntry'},
            'deductions': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            'dq_reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'dq_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'entry_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'entry_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'final_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'grand_total': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number_of_runs_completed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'points_earned': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['races.Race']"}),
            'racer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['racers.Racer']"}),
            'scratch_pad': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'supplementary_points': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'})
        },
        u'racers.racer': {
            'Meta': {'object_name': 'Racer'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'nick_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'racer_number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'races.race': {
            'Meta': {'object_name': 'Race'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'race_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'race_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['raceentries']