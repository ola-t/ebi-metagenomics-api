# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-09-17 13:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def populate_assemblies(apps, schema_editor):
    Run = apps.get_model("emgapi", "Run")
    Assembly = apps.get_model("emgapi", "Assembly")
    AnalysisJob = apps.get_model("emgapi", "AnalysisJob")
    ExperimentType = apps.get_model("emgapi", "ExperimentType")
    experiment_type = ExperimentType.objects.get(experiment_type="assembly")
    AssemblyMapping = apps.get_model("emgena", "AssemblyMapping")

    # total = Run.objects.filter(experiment_type=experiment_type).count()
    for run in Run.objects.filter(experiment_type=experiment_type):
        #print(run.accession)
        try:
            _assembly = AssemblyMapping.objects.using('ena_pro') \
                .get(legacy_accession=run.accession)
        except AssemblyMapping.DoesNotExist:
            a = Assembly.objects.create(
                accession=run.accession,
                legacy_accession=run.secondary_accession,
                status_id=run.status_id,
                sample=run.sample,
                study=run.study,
                experiment_type=experiment_type,
            )
        except AssemblyMapping.MultipleObjectsReturned:
            a = Assembly.objects.create(
                accession=run.accession,
                legacy_accession=run.secondary_accession,
                status_id=run.status_id,
                sample=run.sample,
                study=run.study,
                experiment_type=experiment_type,
            )
        else:
            a = Assembly.objects.create(
                accession=_assembly.accession,
                legacy_accession=_assembly.legacy_accession,
                wgs_accession=_assembly.wgs_accession,
                status_id=run.status_id,
                sample=run.sample,
                study=run.study,
                experiment_type=experiment_type,
            )
        for aj in AnalysisJob.objects.filter(run=run):
            aj.run = None
            aj.assembly = a
            aj.save()
        if aj.external_run_ids == run.accession:
            run.delete()
        else:
            print(aj.accesion, run.accession)

# def delete_duplicated(apps, schema_editor):
#     Run = apps.get_model("emgapi", "Run")
#     ExperimentType = apps.get_model("emgapi", "ExperimentType")
#     experiment_type = ExperimentType.objects.get(experiment_type="assembly")
#
#     for run in Run.objects.filter(experiment_type=experiment_type):
#         run.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('emgapi', '0009_remove_gsccvcv'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assembly',
            fields=[
                ('assembly_id', models.BigAutoField(db_column='ASSEMBLY_ID', primary_key=True, serialize=False)),
                ('accession', models.CharField(blank=True, db_column='ACCESSION', max_length=80, null=True)),
                ('wgs_accession', models.CharField(blank=True, db_column='WGS_ACCESSION', max_length=100, null=True)),
                ('legacy_accession', models.CharField(blank=True, db_column='LEGACY_ACCESSION', max_length=100, null=True)),
            ],
            options={
                'db_table': 'ASSEMBLY',
                'ordering': ('accession',),
            },
        ),
        migrations.AddField(
            model_name='assembly',
            name='experiment_type',
            field=models.ForeignKey(blank=True, db_column='EXPERIMENT_TYPE_ID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assemblies', to='emgapi.ExperimentType'),
        ),
        migrations.AddField(
            model_name='assembly',
            name='sample',
            field=models.ForeignKey(blank=True, db_column='SAMPLE_ID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assemblies', to='emgapi.Sample'),
        ),
        migrations.AddField(
            model_name='assembly',
            name='status_id',
            field=models.ForeignKey(db_column='STATUS_ID', default=2, on_delete=django.db.models.deletion.CASCADE, related_name='assemblies', to='emgapi.Status'),
        ),
        migrations.AddField(
            model_name='assembly',
            name='study',
            field=models.ForeignKey(blank=True, db_column='STUDY_ID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assemblies', to='emgapi.Study'),
        ),
        migrations.AlterUniqueTogether(
            name='assembly',
            unique_together=set([('accession', 'wgs_accession', 'legacy_accession'), ('assembly_id', 'accession')]),
        ),

        migrations.AddField(
            model_name='analysisjob',
            name='assembly',
            field=models.ForeignKey(blank=True, db_column='ASSEMBLY_ID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='analyses', to='emgapi.Assembly'),
        ),

        migrations.RunPython(populate_assemblies),
        #migrations.RunPython(delete_duplicated),

    ]