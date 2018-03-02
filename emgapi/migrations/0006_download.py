# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-27 13:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def create_group_types(apps, schema_editor):
    DownloadGroupType = apps.get_model("emgapi", "DownloadGroupType")
    group_types = (
        "Sequence data",
        "Functional analysis",
        "Taxonomic analysis",
        "Taxonomic analysis SSU rRNA",
        "Taxonomic analysis LSU rRNA",
        "Statistics",
    )
    _groups = list()
    for group_type in group_types:
        _groups.append(
            DownloadGroupType(group_type=group_type)
        )
    DownloadGroupType.objects.bulk_create(_groups)


def create_fileformats(apps, schema_editor):
    FileFormat = apps.get_model("emgapi", "FileFormat")
    file_formats = (
        ("TSV", "tsv"),
        ("CSV", "csv"),
        ("FASTA", "fasta"),
        ("Biom", "biom"),
        ("HDF5 Biom", "biom"),
        ("JSON Biom", "biom"),
        ("Newick format", "tree"),
    )
    _formats = list()
    for file_format in file_formats:
        _formats.append(
            FileFormat(
                format_name=file_format[0],
                format_extention=file_format[1]
            )
        )
    FileFormat.objects.bulk_create(_formats)


class Migration(migrations.Migration):

    dependencies = [
        ('emgapi', '0005_study_sample_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='pipeline',
            name='tools',
            field=models.ManyToManyField(related_name='pipelines', through='emgapi.PipelineReleaseTool', to='emgapi.PipelineTool'),
        ),
        migrations.AddField(
            model_name='study',
            name='publications',
            field=models.ManyToManyField(related_name='studies', through='emgapi.StudyPublication', to='emgapi.Publication'),
        ),
        migrations.AddField(
            model_name='study',
            name='samples',
            field=models.ManyToManyField(blank=True, related_name='studies', through='emgapi.StudySample', to='emgapi.Sample'),
        ),
        migrations.AlterField(
            model_name='analysisjob',
            name='sample',
            field=models.ForeignKey(blank=True, db_column='SAMPLE_ID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='analysis', to='emgapi.Sample'),
        ),
        migrations.AlterField(
            model_name='analysisjob',
            name='study',
            field=models.ForeignKey(blank=True, db_column='STUDY_ID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='analysis', to='emgapi.Study'),
        ),

        migrations.AlterField(
            model_name='pipeline',
            name='pipeline_id',
            field=models.SmallIntegerField(db_column='PIPELINE_ID', primary_key=True, serialize=False),
        ),

        migrations.CreateModel(
            name='AnalysisJobDownload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('realname', models.CharField(db_column='REAL_NAME', max_length=255)),
                ('alias', models.CharField(db_column='ALIAS', max_length=255)),
            ],
            options={
                'db_table': 'ANALYSIS_JOB_DOWNLOAD',
            },
        ),
        migrations.CreateModel(
            name='DownloadDescriptionLabel',
            fields=[
                ('description_id', models.AutoField(db_column='DESCRIPTION_ID', primary_key=True, serialize=False)),
                ('description', models.CharField(db_column='DESCRIPTION', max_length=255)),
                ('description_label', models.CharField(db_column='DESCRIPTION_LABEL', max_length=50)),
            ],
            options={
                'db_table': 'DOWNLOAD_DESCRIPTION_LABEL',
            },
        ),
        migrations.CreateModel(
            name='DownloadGroupType',
            fields=[
                ('group_id', models.AutoField(db_column='GROUP_ID', primary_key=True, serialize=False)),
                ('group_type', models.CharField(db_column='GROUP_TYPE', max_length=30)),
            ],
            options={
                'db_table': 'DOWNLOAD_GROUP_TYPE',
            },
        ),
        migrations.CreateModel(
            name='DownloadSubdir',
            fields=[
                ('subdir_id', models.AutoField(db_column='SUBDIR_ID', primary_key=True, serialize=False)),
                ('subdir', models.CharField(db_column='SUBDIR', max_length=100)),
            ],
            options={
                'db_table': 'DOWNLOAD_SUBDIR',
            },
        ),
        migrations.CreateModel(
            name='FileFormat',
            fields=[
                ('format_id', models.AutoField(db_column='FORMAT_ID', primary_key=True, serialize=False)),
                ('format_name', models.CharField(db_column='FORMAT_NAME', max_length=30)),
                ('format_extention', models.CharField(db_column='FORMAT_EXTENTION', max_length=30)),
            ],
            options={
                'db_table': 'FILE_FORMAT',
            },
        ),
        migrations.CreateModel(
            name='StudyDownload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('realname', models.CharField(db_column='REAL_NAME', max_length=255)),
                ('alias', models.CharField(db_column='ALIAS', max_length=255)),
                ('description', models.ForeignKey(blank=True, db_column='DESCRIPTION_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='emgapi.DownloadDescriptionLabel')),
                ('file_format', models.ForeignKey(blank=True, db_column='FORMAT_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='emgapi.FileFormat')),
                ('group_type', models.ForeignKey(blank=True, db_column='GROUP_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='emgapi.DownloadGroupType')),
                ('parent_id', models.ForeignKey(blank=True, db_column='PARENT_DOWNLOAD_ID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent', to='emgapi.StudyDownload')),
            ],
            options={
                'db_table': 'STUDY_DOWNLOAD',
            },
        ),

        migrations.AddField(
            model_name='studydownload',
            name='pipeline',
            field=models.ForeignKey(blank=True, db_column='PIPELINE_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='emgapi.Pipeline'),
        ),
        migrations.AddField(
            model_name='studydownload',
            name='study',
            field=models.ForeignKey(db_column='STUDY_ID', on_delete=django.db.models.deletion.CASCADE, related_name='study_download', to='emgapi.Study'),
        ),
        migrations.AddField(
            model_name='studydownload',
            name='subdir',
            field=models.ForeignKey(blank=True, db_column='SUBDIR_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='emgapi.DownloadSubdir'),
        ),
        migrations.AddField(
            model_name='analysisjobdownload',
            name='description',
            field=models.ForeignKey(blank=True, db_column='DESCRIPTION_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='emgapi.DownloadDescriptionLabel'),
        ),
        migrations.AddField(
            model_name='analysisjobdownload',
            name='file_format',
            field=models.ForeignKey(blank=True, db_column='FORMAT_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='emgapi.FileFormat'),
        ),
        migrations.AddField(
            model_name='analysisjobdownload',
            name='group_type',
            field=models.ForeignKey(blank=True, db_column='GROUP_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='emgapi.DownloadGroupType'),
        ),
        migrations.AddField(
            model_name='analysisjobdownload',
            name='job',
            field=models.ForeignKey(db_column='JOB_ID', on_delete=django.db.models.deletion.CASCADE, related_name='analysis_download', to='emgapi.AnalysisJob'),
        ),
        migrations.AddField(
            model_name='analysisjobdownload',
            name='parent_id',
            field=models.ForeignKey(blank=True, db_column='PARENT_DOWNLOAD_ID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent', to='emgapi.AnalysisJobDownload'),
        ),
        migrations.AddField(
            model_name='analysisjobdownload',
            name='pipeline',
            field=models.ForeignKey(blank=True, db_column='PIPELINE_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='emgapi.Pipeline'),
        ),
        migrations.AddField(
            model_name='analysisjobdownload',
            name='subdir',
            field=models.ForeignKey(blank=True, db_column='SUBDIR_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='emgapi.DownloadSubdir'),
        ),
        migrations.AlterUniqueTogether(
            name='studydownload',
            unique_together=set([('realname', 'alias')]),
        ),
        migrations.AlterUniqueTogether(
            name='analysisjobdownload',
            unique_together=set([('realname', 'alias')]),
        ),
        migrations.RunPython(create_group_types),
        migrations.RunPython(create_fileformats),
    ]
