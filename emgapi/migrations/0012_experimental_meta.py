# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-13 17:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('emgapi', '0011_study_is_public'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysisjobann',
            name='job',
            field=models.ForeignKey(db_column='JOB_ID', on_delete=django.db.models.deletion.CASCADE, related_name='analysis_annotation', to='emgapi.AnalysisJob'),
        ),
        migrations.AlterField(
            model_name='analysisjobann',
            name='var',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analysis_annotation', to='emgapi.AnalysisMetadataVariableNames'),
        ),

        migrations.CreateModel(
            name='AnalysisJobMetadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('units', models.CharField(blank=True, db_column='UNITS', max_length=25, null=True)),
                ('var_val_ucv', models.CharField(blank=True, db_column='VAR_VAL_UCV', max_length=4000, null=True)),
            ],
            options={
                'db_table': 'ANALYSIS_JOB_METADATA',
            },
        ),

        migrations.AddField(
            model_name='analysisjobmetadata',
            name='job',
            field=models.ForeignKey(db_column='JOB_ID', on_delete=django.db.models.deletion.CASCADE, related_name='analysis_metadata', to='emgapi.AnalysisJob'),
        ),
        migrations.AddField(
            model_name='analysisjobmetadata',
            name='var',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analysis_metadata', to='emgapi.AnalysisMetadataVariableNames'),
        ),
        migrations.AlterUniqueTogether(
            name='analysisjobmetadata',
            unique_together=set([('job', 'var')]),
        ),
    
        migrations.RunSQL(
            """INSERT INTO SUMMARY_VARIABLE_NAMES (VAR_NAME)
               VALUES ('Variable Region');"""
        ),
    ]
