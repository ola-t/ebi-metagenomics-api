# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-07-15 09:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('emgapi', '0014_study_publication_pk_fix'),
    ]

    operations = [
        migrations.CreateModel(
            name='SuperStudy',
            fields=[
                ('super_study_id', models.AutoField(db_column='STUDY_ID', primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, db_column='TITLE', max_length=100, null=True)),
                ('description', models.TextField(db_column='DESCRIPTION')),
            ],
            options={
                'verbose_name_plural': 'super_studies',
                'db_table': 'SUPER_STUDY',
            },
        ),
        migrations.CreateModel(
            name='SuperStudyBiome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('biome', models.ForeignKey(db_column='BIOME_ID', on_delete=django.db.models.deletion.CASCADE, to='emgapi.Biome')),
                ('super_study', models.ForeignKey(db_column='SUPER_STUDY_ID', on_delete=django.db.models.deletion.CASCADE, to='emgapi.SuperStudy')),
            ],
            options={
                'verbose_name_plural': 'super studies biomes',
                'db_table': 'SUPER_STUDY_BIOME',
            },
        ),
        migrations.CreateModel(
            name='SuperStudyStudy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'super studies studies',
                'db_table': 'SUPER_STUDY_STUDY',
            },
        ),
        migrations.AlterModelOptions(
            name='study',
            options={'ordering': ('study_id',), 'verbose_name_plural': 'studies'},
        ),
        migrations.AddField(
            model_name='superstudystudy',
            name='study',
            field=models.ForeignKey(db_column='STUDY_ID', on_delete=django.db.models.deletion.CASCADE, to='emgapi.Study'),
        ),
        migrations.AddField(
            model_name='superstudystudy',
            name='super_study',
            field=models.ForeignKey(db_column='SUPER_STUDY_ID', on_delete=django.db.models.deletion.CASCADE, to='emgapi.SuperStudy'),
        ),
        migrations.AddField(
            model_name='superstudy',
            name='biomes',
            field=models.ManyToManyField(blank=True, related_name='super_studies', through='emgapi.SuperStudyBiome', to='emgapi.Biome'),
        ),
        migrations.AddField(
            model_name='superstudy',
            name='flagship_studies',
            field=models.ManyToManyField(blank=True, related_name='super_studies', through='emgapi.SuperStudyStudy', to='emgapi.Study'),
        ),
        migrations.AlterUniqueTogether(
            name='superstudystudy',
            unique_together=set([('study', 'super_study')]),
        ),
        migrations.AlterUniqueTogether(
            name='superstudybiome',
            unique_together=set([('biome', 'super_study')]),
        ),

        migrations.RunSQL(
            sql='CREATE FULLTEXT INDEX super_study_title_ts_idx ON SUPER_STUDY(title)',
            reverse_sql='ALTER TABLE SUPER_STUDY DROP INDEX super_study_title_ts_idx',
        ),
        migrations.RunSQL(
            sql='CREATE FULLTEXT INDEX super_study_description_ts_idx ON SUPER_STUDY(description)',
            reverse_sql='ALTER TABLE SUPER_STUDY DROP INDEX super_study_description_ts_idx',
        ),
    ]
