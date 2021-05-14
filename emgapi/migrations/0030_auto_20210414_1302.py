# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-14 13:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('emgapi', '0029_auto_20201022_1359'),
    ]

    operations = [
        migrations.AddField(
            model_name='assembly',
            name='coverage',
            field=models.IntegerField(blank=True, db_column='COVERAGE', null=True),
        ),
        migrations.AddField(
            model_name='assembly',
            name='min_gap_length',
            field=models.IntegerField(blank=True, db_column='MIN_GAP_LENGTH', null=True),
        ),
        migrations.AddField(
            model_name='assembly',
            name='study',
            field=models.ForeignKey(blank=True, db_column='STUDY_ID', null=True, on_delete=django.db.models.deletion.SET_NULL, to='emgapi.Study'),
        ),
    ]
