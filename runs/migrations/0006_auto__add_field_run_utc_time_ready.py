# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Run.utc_time_ready'
        db.add_column(u'runs_run', 'utc_time_ready',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Run.utc_time_ready'
        db.delete_column(u'runs_run', 'utc_time_ready')


    models = {
        u'checkpoints.checkpoint': {
            'Meta': {'object_name': 'Checkpoint'},
            'checkpoint_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'checkpoint_number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'jobs.job': {
            'Meta': {'object_name': 'Job'},
            'drop_checkpoint': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'drop'", 'to': u"orm['checkpoints.Checkpoint']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'manifest': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['races.Manifest']", 'null': 'True', 'blank': 'True'}),
            'minutes_due_after_start': ('django.db.models.fields.IntegerField', [], {'default': '9999'}),
            'minutes_ready_after_start': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pick_checkpoint': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pick'", 'to': u"orm['checkpoints.Checkpoint']"}),
            'points': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['races.Race']"})
        },
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
        u'races.manifest': {
            'Meta': {'object_name': 'Manifest'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manifest_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['races.Race']"})
        },
        u'races.race': {
            'Meta': {'object_name': 'Race'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'race_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'race_start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'race_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'runs.run': {
            'Meta': {'ordering': "['job__minutes_ready_after_start']", 'object_name': 'Run'},
            'completion_seconds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'determination': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jobs.Job']"}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'points_awarded': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            'race_entry': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['raceentries.RaceEntry']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'time_entered': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'utc_time_dropped': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'utc_time_picked': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'utc_time_ready': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['runs']