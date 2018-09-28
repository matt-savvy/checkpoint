# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Manifest', fields ['manifest_name', 'race']
        db.create_unique(u'races_manifest', ['manifest_name', 'race_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Manifest', fields ['manifest_name', 'race']
        db.delete_unique(u'races_manifest', ['manifest_name', 'race_id'])


    models = {
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
            'race_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['races']