# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Run'
        db.create_table(u'runs_run', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('run_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jobs.Job'])),
            ('racer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['racers.Racer'])),
            ('ticket_number', self.gf('django.db.models.fields.IntegerField')()),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'runs', ['Run'])


    def backwards(self, orm):
        # Deleting model 'Run'
        db.delete_table(u'runs_run')


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
            'pick_checkpoint': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pick'", 'to': u"orm['checkpoints.Checkpoint']"}),
            'points': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['races.Race']"})
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
        },
        u'runs.run': {
            'Meta': {'object_name': 'Run'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jobs.Job']"}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'racer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['racers.Racer']"}),
            'run_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ticket_number': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['runs']