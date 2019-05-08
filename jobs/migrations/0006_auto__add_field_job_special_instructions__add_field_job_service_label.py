# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Job.special_instructions'
        db.add_column(u'jobs_job', 'special_instructions',
                      self.gf('django.db.models.fields.CharField')(max_length=144, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Job.service_label'
        db.add_column(u'jobs_job', 'service_label',
                      self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Job.special_instructions'
        db.delete_column(u'jobs_job', 'special_instructions')

        # Deleting field 'Job.service_label'
        db.delete_column(u'jobs_job', 'service_label')


    models = {
        u'checkpoints.checkpoint': {
            'Meta': {'ordering': "['checkpoint_number']", 'object_name': 'Checkpoint'},
            'address_line_1': ('django.db.models.fields.CharField', [], {'max_length': '144', 'null': 'True', 'blank': 'True'}),
            'address_line_2': ('django.db.models.fields.CharField', [], {'max_length': '144', 'null': 'True', 'blank': 'True'}),
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
            'minutes_due_after_start': ('django.db.models.fields.IntegerField', [], {'default': '180'}),
            'minutes_ready_after_start': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pick_checkpoint': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pick'", 'to': u"orm['checkpoints.Checkpoint']"}),
            'points': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['races.Race']"}),
            'service_label': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'special_instructions': ('django.db.models.fields.CharField', [], {'max_length': '144', 'null': 'True', 'blank': 'True'})
        },
        u'races.manifest': {
            'Meta': {'ordering': "['manifest_type']", 'unique_together': "(('manifest_name', 'race'),)", 'object_name': 'Manifest'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manifest_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'manifest_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['races.Race']"})
        },
        u'races.race': {
            'Meta': {'object_name': 'Race'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overtime': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'race_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'race_start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'race_type': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['jobs']