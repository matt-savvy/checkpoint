# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Manifest.cut_off_minutes_after_start'
        db.add_column(u'races_manifest', 'cut_off_minutes_after_start',
                      self.gf('django.db.models.fields.IntegerField')(default=9999),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Manifest.cut_off_minutes_after_start'
        db.delete_column(u'races_manifest', 'cut_off_minutes_after_start')


    models = {
        u'races.manifest': {
            'Meta': {'ordering': "['manifest_type', 'order']", 'object_name': 'Manifest'},
            'cut_off_minutes_after_start': ('django.db.models.fields.IntegerField', [], {'default': '9999'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manifest_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'manifest_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['races.Race']"})
        },
        u'races.race': {
            'Meta': {'object_name': 'Race'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'race_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'race_start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'race_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['races']