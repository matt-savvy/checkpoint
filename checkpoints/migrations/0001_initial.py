# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Checkpoint'
        db.create_table(u'checkpoints_checkpoint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('checkpoint_number', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('checkpoint_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'checkpoints', ['Checkpoint'])


    def backwards(self, orm):
        # Deleting model 'Checkpoint'
        db.delete_table(u'checkpoints_checkpoint')


    models = {
        u'checkpoints.checkpoint': {
            'Meta': {'object_name': 'Checkpoint'},
            'checkpoint_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'checkpoint_number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['checkpoints']