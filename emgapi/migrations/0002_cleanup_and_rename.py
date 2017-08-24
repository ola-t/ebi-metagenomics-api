# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-29 10:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('emgapi', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BiomeHierarchyTree',
            new_name='Biome',
        ),
        migrations.RenameModel(
            old_name='PipelineRelease',
            new_name='Pipeline',
        ),
        # migrations.RenameModel(
        #     old_name='AnalysisJob',
        #     new_name='Run',
        # ),
        migrations.RenameField(
            model_name='analysisjob',
            old_name='external_run_ids',
            new_name='accession',
        ),
        migrations.AlterField(
            model_name='analysisjob',
            name='accession',
            field=models.CharField(db_column='EXTERNAL_RUN_IDS', max_length=100),
        ),
        migrations.RemoveField(
            model_name='analysisjob',
            name='re_run_count',
        ),
        migrations.RemoveField(
            model_name='analysisjob',
            name='is_production_run',
        ),
        migrations.RenameField(
            model_name='sample',
            old_name='ext_sample_id',
            new_name='accession',
        ),
        migrations.AlterField(
            model_name='sample',
            name='accession',
            field=models.CharField(db_column='EXT_SAMPLE_ID', max_length=20),
        ),
        migrations.RenameField(
            model_name='study',
            old_name='ext_study_id',
            new_name='accession',
        ),
        migrations.AlterField(
            model_name='study',
            name='accession',
            field=models.CharField(db_column='EXT_STUDY_ID', max_length=20, unique=True),
        ),
        migrations.RemoveField(
            model_name='study',
            name='experimental_factor',
        ),
        migrations.RemoveField(
            model_name='study',
            name='ncbi_project_id',
        ),
        migrations.AlterField(
            model_name='pipelinereleasetool',
            name='how_tool_used_desc',
            field=models.TextField(blank=True, db_column='HOW_TOOL_USED_DESC', null=True),
        ),
        migrations.AlterField(
            model_name='pipelinereleasetool',
            name='pipeline',
            field=models.ForeignKey(db_column='PIPELINE_ID', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='emgapi.Pipeline'),
        ),
        migrations.AlterField(
            model_name='pipelinereleasetool',
            name='tool',
            field=models.ForeignKey(db_column='TOOL_ID', on_delete=django.db.models.deletion.CASCADE, to='emgapi.PipelineTool'),
        ),
        migrations.AlterField(
            model_name='pipelinetool',
            name='description',
            field=models.TextField(blank=True, db_column='DESCRIPTION', null=True),
        ),
        migrations.AlterField(
            model_name='pipelinetool',
            name='exe_command',
            field=models.CharField(blank=True, db_column='EXE_COMMAND', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='pipelinetool',
            name='tool_name',
            field=models.CharField(blank=True, db_column='TOOL_NAME', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='pipelinetool',
            name='version',
            field=models.CharField(blank=True, db_column='VERSION', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='analysisjob',
            name='analysis_status',
            field=models.ForeignKey(db_column='ANALYSIS_STATUS_ID', on_delete=django.db.models.deletion.CASCADE, to='emgapi.AnalysisStatus'),
        ),
        migrations.AlterField(
            model_name='analysisjob',
            name='experiment_type',
            field=models.ForeignKey(db_column='EXPERIMENT_TYPE_ID', on_delete=django.db.models.deletion.CASCADE, related_name='analysis', to='emgapi.ExperimentType'),
        ),
        migrations.AlterField(
            model_name='analysisjob',
            name='pipeline',
            field=models.ForeignKey(db_column='PIPELINE_ID', on_delete=django.db.models.deletion.CASCADE, related_name='analysis', to='emgapi.Pipeline'),
        ),
        migrations.AlterField(
            model_name='analysisjob',
            name='sample',
            field=models.ForeignKey(db_column='SAMPLE_ID', on_delete=django.db.models.deletion.CASCADE, related_name='analysis', to='emgapi.Sample'),
        ),
        migrations.AlterField(
            model_name='sample',
            name='accession',
            field=models.CharField(db_column='EXT_SAMPLE_ID', max_length=20),
        ),
        migrations.AlterField(
            model_name='sample',
            name='biome',
            field=models.ForeignKey(db_column='BIOME_ID', on_delete=django.db.models.deletion.CASCADE, related_name='samples', to='emgapi.Biome'),
        ),
        migrations.AlterField(
            model_name='sample',
            name='study',
            field=models.ForeignKey(db_column='STUDY_ID', on_delete=django.db.models.deletion.CASCADE, related_name='samples', to='emgapi.Study'),
        ),
        migrations.AlterField(
            model_name='samplepublication',
            name='pub',
            field=models.ForeignKey(db_column='PUB_ID', on_delete=django.db.models.deletion.CASCADE, to='emgapi.Publication'),
        ),
        migrations.AlterField(
            model_name='samplepublication',
            name='sample',
            field=models.ForeignKey(db_column='SAMPLE_ID', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='emgapi.Sample'),
        ),
        migrations.AlterField(
            model_name='study',
            name='biome',
            field=models.ForeignKey(db_column='BIOME_ID', on_delete=django.db.models.deletion.CASCADE, related_name='studies', to='emgapi.Biome'),
        ),
        migrations.AlterField(
            model_name='studypublication',
            name='pub',
            field=models.ForeignKey(db_column='PUB_ID', on_delete=django.db.models.deletion.CASCADE, to='emgapi.Publication'),
        ),
        migrations.AlterField(
            model_name='studypublication',
            name='study',
            field=models.ForeignKey(db_column='STUDY_ID', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='emgapi.Study'),
        ),
        migrations.AlterModelOptions(
            name='analysisstatus',
            options={'ordering': ('analysis_status_id',)},
        ),
        migrations.AlterModelOptions(
            name='biome',
            options={'ordering': ('biome_id',)},
        ),
        migrations.AlterModelOptions(
            name='pipeline',
            options={'ordering': ('release_version',)},
        ),
        migrations.AlterModelOptions(
            name='publication',
            options={'ordering': ('pubmed_id',)},
        ),
        migrations.AlterModelOptions(
            name='analysisjob',
            options={'ordering': ('accession',)},
        ),
        migrations.AlterModelOptions(
            name='sample',
            options={'ordering': ('accession',)},
        ),
        migrations.AlterModelOptions(
            name='study',
            options={'ordering': ('accession',)},
        ),
        migrations.AlterUniqueTogether(
            name='pipeline',
            unique_together=set([('pipeline_id', 'release_version')]),
        ),
        migrations.AlterUniqueTogether(
            name='pipelinereleasetool',
            unique_together=set([('pipeline', 'tool'), ('pipeline', 'tool_group_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='pipelinetool',
            unique_together=set([('tool_name', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='biome',
            unique_together=set([('biome_id', 'biome_name')]),
        ),
        # Ticket: IBU-6868
        # combine external_run_id/accession and pipeline version
        # to restrict duplicates
        migrations.AlterUniqueTogether(
            name='analysisjob',
            unique_together=set([('job_id', 'accession'), ('pipeline', 'accession')]),
        ),
        migrations.AlterUniqueTogether(
            name='sample',
            unique_together=set([('sample_id', 'accession')]),
        ),
        migrations.AlterUniqueTogether(
            name='samplepublication',
            unique_together=set([('sample', 'pub')]),
        ),
        migrations.AlterUniqueTogether(
            name='study',
            unique_together=set([('study_id', 'accession')]),
        ),
        migrations.AlterUniqueTogether(
            name='studypublication',
            unique_together=set([('study', 'pub')]),
        ),
        migrations.RunSQL(
            sql='CREATE FULLTEXT INDEX biome_biome_name_ts_idx ON BIOME_HIERARCHY_TREE (biome_name)',
            reverse_sql='ALTER TABLE BIOME_HIERARCHY_TREE DROP INDEX biome_biome_name_ts_idx',
        ),
        migrations.RunSQL(
            sql='CREATE FULLTEXT INDEX study_study_name_ts_idx ON STUDY(study_name)',
            reverse_sql='ALTER TABLE STUDY DROP INDEX study_study_name_ts_idx',
        ),
        migrations.RunSQL(
            sql='CREATE FULLTEXT INDEX study_study_abstract_ts_idx ON STUDY (study_abstract)',
            reverse_sql='ALTER TABLE STUDY DROP INDEX study_study_abstract_ts_idx',
        ),
        migrations.RunSQL(
            sql='CREATE FULLTEXT INDEX publication_publication_title_ts_idx ON PUBLICATION (pub_title)',
            reverse_sql='ALTER TABLE PUBLICATION DROP INDEX publication_publication_title_ts_idx',
        ),
        migrations.RunSQL(
            sql='CREATE FULLTEXT INDEX publication_pub_abstract_ts_idx ON PUBLICATION (pub_abstract)',
            reverse_sql='ALTER TABLE PUBLICATION DROP INDEX publication_pub_abstract_ts_idx',
        ),
        migrations.RunSQL(
            sql='CREATE FULLTEXT INDEX pipeline_description_ts_idx ON PIPELINE_RELEASE (description)',
            reverse_sql='ALTER TABLE PIPELINE_RELEASE DROP INDEX pipeline_description_ts_idx',
        ),
        migrations.RunSQL(
            sql='CREATE FULLTEXT INDEX pipeline_changes_ts_idx ON PIPELINE_RELEASE (changes)',
            reverse_sql='ALTER TABLE PIPELINE_RELEASE DROP INDEX pipeline_changes_ts_idx',
        ),
        migrations.RunSQL(
            sql='CREATE FULLTEXT INDEX sample_sample_name_ts_idx ON SAMPLE (sample_name)',
            reverse_sql='ALTER TABLE SAMPLE DROP INDEX sample_sample_name_ts_idx',
        ),
        migrations.RunSQL(
            sql='CREATE FULLTEXT INDEX sample_sample_desc_ts_idx ON SAMPLE (sample_desc)',
            reverse_sql='ALTER TABLE SAMPLE DROP INDEX sample_sample_desc_ts_idx',
        ),
        migrations.RunSQL(
            sql='CREATE FULLTEXT INDEX sample_ann_var_val_ucv_ts_idx ON SAMPLE_ANN (var_val_ucv)',
            reverse_sql='ALTER TABLE SAMPLE_ANN DROP INDEX sample_ann_var_val_ucv_ts_idx',
        ),
        migrations.RunSQL(
            sql='CREATE FULLTEXT INDEX run_instrument_platform_ts_idx ON ANALYSIS_JOB (instrument_platform)',
            reverse_sql='ALTER TABLE ANALYSIS_JOB DROP INDEX run_instrument_platform_ts_idx',
        ),
        migrations.RunSQL(
            sql='CREATE FULLTEXT INDEX run_instrument_model_ts_idx ON ANALYSIS_JOB (instrument_model)',
            reverse_sql='ALTER TABLE ANALYSIS_JOB DROP INDEX run_instrument_model_ts_idx',
        ),
    ]
