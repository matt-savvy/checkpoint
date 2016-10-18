# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StreamEvent'
        db.create_table(u'streamer_streamevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('racer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['racers.Racer'])),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('message_photo', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('poster_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('poster_photo', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'streamer', ['StreamEvent'])


    def backwards(self, orm):
        # Deleting model 'StreamEvent'
        db.delete_table(u'streamer_streamevent')


    models = {
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
        u'streamer.streamevent': {
            'Meta': {'object_name': 'StreamEvent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'message_photo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'poster_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'poster_photo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'racer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['racers.Racer']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['streamer']