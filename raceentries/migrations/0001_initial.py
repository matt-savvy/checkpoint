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
            ('last_action', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('entry_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('starting_position', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('final_time', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('dq_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('dq_reason', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('points_earned', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=8, decimal_places=2)),
            ('supplementary_points', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=8, decimal_places=2)),
            ('deductions', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=8, decimal_places=2)),
            ('grand_total', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=8, decimal_places=2)),
            ('number_of_runs_completed', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('scratch_pad', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('manifest', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['races.Manifest'], null=True, blank=True)),
        ))
        db.send_create_signal(u'raceentries', ['RaceEntry'])

        # Adding unique constraint on 'RaceEntry', fields ['racer', 'race']
        db.create_unique(u'raceentries_raceentry', ['racer_id', 'race_id'])

        # Adding unique constraint on 'RaceEntry', fields ['race', 'starting_position']
        db.create_unique(u'raceentries_raceentry', ['race_id', 'starting_position'])


    def backwards(self, orm):
        # Removing unique constraint on 'RaceEntry', fields ['race', 'starting_position']
        db.delete_unique(u'raceentries_raceentry', ['race_id', 'starting_position'])

        # Removing unique constraint on 'RaceEntry', fields ['racer', 'race']
        db.delete_unique(u'raceentries_raceentry', ['racer_id', 'race_id'])

        # Deleting model 'RaceEntry'
        db.delete_table(u'raceentries_raceentry')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'checkpoints.checkpoint': {
            'Meta': {'ordering': "['checkpoint_number']", 'object_name': 'Checkpoint'},
            'address_line_1': ('django.db.models.fields.CharField', [], {'max_length': '144', 'null': 'True', 'blank': 'True'}),
            'address_line_2': ('django.db.models.fields.CharField', [], {'max_length': '144', 'null': 'True', 'blank': 'True'}),
            'checkpoint_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'checkpoint_number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'open_late': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'companies.company': {
            'Meta': {'object_name': 'Company'},
            'dispatcher': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nacccusers.NACCCUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'nacccusers.nacccuser': {
            'Meta': {'object_name': 'NACCCUser'},
            'authorized_checkpoints': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['checkpoints.Checkpoint']", 'symmetrical': 'False', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'raceentries.raceentry': {
            'Meta': {'ordering': "['starting_position']", 'unique_together': "(('racer', 'race'), ('race', 'starting_position'))", 'object_name': 'RaceEntry'},
            'deductions': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            'dq_reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'dq_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'entry_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'entry_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'final_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'grand_total': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_action': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'manifest': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['races.Manifest']", 'null': 'True', 'blank': 'True'}),
            'number_of_runs_completed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'points_earned': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['races.Race']"}),
            'racer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['racers.Racer']"}),
            'scratch_pad': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'starting_position': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'supplementary_points': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '8', 'decimal_places': '2'})
        },
        u'racers.racer': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'Racer'},
            'cargo': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['companies.Company']"}),
            'contact_info': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '50', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'heat': ('django.db.models.fields.CharField', [], {'default': "'a'", 'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'nick_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'packet': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paypal_tx': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'racer_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'radio_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'shirt_size': ('django.db.models.fields.CharField', [], {'default': "'M'", 'max_length': '2'}),
            'team': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'track': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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

    complete_apps = ['raceentries']