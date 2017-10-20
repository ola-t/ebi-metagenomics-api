# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-05 16:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('emgapi', '0004_analysisjobann'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysisjob',
            name='sample',
            field=models.ForeignKey(blank=True, db_column='SAMPLE_ID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='analysis', to='emgapi.Sample'),
        ),
        migrations.AlterField(
            model_name='sample',
            name='study',
            field=models.ForeignKey(blank=True, db_column='STUDY_ID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='samples', to='emgapi.Study'),
        ),
        migrations.AlterField(
            model_name='sample',
            name='accession',
            field=models.CharField(db_column='EXT_SAMPLE_ID', max_length=20, unique=True),
        ),
    ]
