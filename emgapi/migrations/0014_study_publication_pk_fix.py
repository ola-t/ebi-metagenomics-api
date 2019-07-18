# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-07-15 16:47
from __future__ import unicode_literals

from django.db import migrations

from django.db import migrations, models
import django


class Migration(migrations.Migration):

    dependencies = [
        ('emgapi', '0013_emgapi_ann_pk_fix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studypublication',
            name='study',
            field=models.ForeignKey(db_column='STUDY_ID', on_delete=django.db.models.deletion.CASCADE, to='emgapi.Study'),
        ),
        migrations.AlterUniqueTogether(
            name='studypublication',
            unique_together=set([]),
        ),
        migrations.AddField(
            model_name='studypublication',
            name='id',
            field=models.IntegerField(null=True),
        ),
        migrations.RunSQL(
            sql='SET @a:=0;UPDATE STUDY_PUBLICATION SET id=@a:=@a+1;',
        ),
        migrations.AlterField(
            model_name='studypublication',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='studypublication',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterUniqueTogether(
            name='studypublication',
            unique_together=set([('study', 'pub')]),
        ),
    ]
