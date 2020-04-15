# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-04-15 10:55
from __future__ import unicode_literals

from django.db import migrations


def create_download_description(apps, schema_editor):
    DownloadDescriptionLabel = apps.get_model("emgapi", "DownloadDescriptionLabel")
    downloads = (
        ("Full antiSMASH sequence features", "Full antiSMASH sequence features",),
    )
    _downloads = list()
    for d in downloads:
        _downloads.append(
            DownloadDescriptionLabel(
                description=d[0],
                description_label=d[1]
            )
        )
    DownloadDescriptionLabel.objects.bulk_create(_downloads)


def create_file_formats(apps, schema_editor):
    FileFormat = apps.get_model("emgapi", "FileFormat")
    file_formats = (
        ("GFF", "gff", True)
    )
    _formats = list()
    for file_format in file_formats:
        _formats.append(
            FileFormat(
                format_name=file_format[0],
                format_extension=file_format[1],
                compression=file_format[2],
            )
        )
    FileFormat.objects.bulk_create(_formats)


def create_subdirs(apps, schema_editor):
    DownloadSubdir = apps.get_model("emgapi", "DownloadSubdir")
    subdirs = (
        "functional-annotation",
        "functional-annotation/stats",
        "pathways-systems",
    )
    _subdirs = list()
    for subdir in subdirs:
        _subdirs.append(
            DownloadSubdir(
                subdir=subdir
            )
        )
    DownloadSubdir.objects.bulk_create(_subdirs)

class Migration(migrations.Migration):

    dependencies = [
        ('emgapi', '0022_auto_20200219_1526'),
    ]

    operations = [
        migrations.RunPython(create_file_formats),
        migrations.RunPython(create_subdirs),
        migrations.RunPython(create_download_description),
    ]