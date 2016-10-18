# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Run.status'
        db.add_column(u'runs_run', 'status',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'Run.determination'
        db.add_column(u'runs_run', 'determination',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'Run.utc_time_picked'
        db.add_column(u'runs_run', 'utc_time_picked',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Run.utc_time_dropped'
        db.add_column(u'runs_run', 'utc_time_dropped',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Run.completion_seconds'
        db.add_column(u'runs_run', 'completion_seconds',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Run.status'
        db.delete_column(u'runs_run', 'status')

        # Deleting field 'Run.determination'
        db.delete_column(u'runs_run', 'determination')

        # Deleting field 'Run.utc_time_picked'
        db.delete_column(u'runs_run', 'utc_time_picked')

        # Deleting field 'Run.utc_time_dropped'
        db.delete_column(u'runs_run', 'utc_time_dropped')

        # Deleting field 'Run.completion_seconds'
        db.delete_column(u'runs_run', 'completion_seconds')


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
            'race_start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'race_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'runs.run': {
            'Meta': {'object_name': 'Run'},
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
            'utc_time_picked': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['runs']