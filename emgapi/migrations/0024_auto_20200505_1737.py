# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-05-05 17:37
from __future__ import unicode_literals

from django.db import migrations
from django.db import transaction


def rename_summary_variable_names(apps, schema_editor):
    """
        Rename label 'Nucleotide sequences' to Reads.
        List of labels to change:
            - Nucleotide sequences with InterProScan match
            - Nucleotide sequences with predicted CDS
            - Nucleotide sequences with predicted RNA
            - Nucleotide sequences with predicted rRNA
    :param apps:
    :param schema_editor:
    :return:
    """
    AnalysisMetadataVariableNames = apps.get_model("emgapi", "AnalysisMetadataVariableNames")

    new_summary_variable_names = (
        ("Nucleotide sequences with InterProScan match", "Reads with InterProScan match"),
        ("Nucleotide sequences with predicted CDS", "Reads with predicted CDS"),
        ("Nucleotide sequences with predicted RNA", "Reads with predicted RNA"),
        ("Nucleotide sequences with predicted rRNA", "Reads with predicted rRNA"),
    )

    # with transaction.atomic():
    #     for v in new_summary_variable_names:
    #         obj = AnalysisMetadataVariableNames.objects.get(
    #             var_name=v[0])
    #         obj.var_name = v[1]
    #         obj.save()


def create_summary_variable_names(apps, schema_editor):
    AnalysisMetadataVariableNames = apps.get_model("emgapi", "AnalysisMetadataVariableNames")
    variable_names = (
        ("Contigs with predicted CDS", None),
        ("Contigs with predicted rRNA", None),
    )
    _variable_names = list()
    for v in variable_names:
        _variable_names.append(
            AnalysisMetadataVariableNames(
                var_name=v[0],
                description=v[1]
            )
        )
    AnalysisMetadataVariableNames.objects.bulk_create(_variable_names)


class Migration(migrations.Migration):
    dependencies = [
        ('emgapi', '0023_auto_20200415_1055'),
    ]

    operations = [
        migrations.RunPython(create_summary_variable_names),
        migrations.RunPython(rename_summary_variable_names),
    ]