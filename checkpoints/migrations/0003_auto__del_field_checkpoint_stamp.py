# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Checkpoint.stamp'
        db.delete_column(u'checkpoints_checkpoint', 'stamp')


    def backwards(self, orm):
        # Adding field 'Checkpoint.stamp'
        db.add_column(u'checkpoints_checkpoint', 'stamp',
                      self.gf('django.db.models.fields.CharField')(default='/static/img/bear.png', max_length=255, null=True),
                      keep_default=False)


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