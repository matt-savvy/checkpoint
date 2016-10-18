# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RaceEntry'
        db.create_table(u'raceentries_raceentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('racer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['racers.Racer'])),
            ('race', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['races.Race'])),
            ('entry_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('entry_status', self.gf('django.db.models.fields.IntegerField')()),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('final_time', self.gf('django.db.models.fields.TimeField')(blank=True)),
            ('dq_time', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('dq_reason', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('points_earned', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=8, decimal_places=2)),
            ('deductions', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=8, decimal_places=2)),
            ('grand_total', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=8, decimal_places=2)),
            ('scratch_pad', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'raceentries', ['RaceEntry'])

        # Adding unique constraint on 'RaceEntry', fields ['racer', 'race']
        db.create_unique(u'raceentries_raceentry', ['racer_id', 'race_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'RaceEntry', fields ['racer', 'race']
        db.delete_unique(u'raceentries_raceentry', ['racer_id', 'race_id'])

        # Deleting model 'RaceEntry'
        db.delete_table(u'raceentries_raceentry')


    models = {
        u'raceentries.raceentry': {
            'Meta': {'unique_together': "(('racer', 'race'),)", 'object_name': 'RaceEntry'},
            'deductions': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            'dq_reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'dq_time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'entry_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'entry_status': ('django.db.models.fields.IntegerField', [], {}),
            'final_time': ('django.db.models.fields.TimeField', [], {'blank': 'True'}),
            'grand_total': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points_earned': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['races.Race']"}),
            'racer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['racers.Racer']"}),
            'scratch_pad': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'})
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
        }
    }

    complete_apps = ['raceentries']