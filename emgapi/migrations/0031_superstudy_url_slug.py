# Generated by Django 3.2 on 2021-06-10 10:05

from django.db import migrations, models
import uuid

from django.utils.text import slugify


def add_url_slug_to_super_studies(apps, schema_editor):
    SuperStudy = apps.get_model("emgapi", "SuperStudy")
    for study in SuperStudy.objects.all():
        study.url_slug = slugify(study.title)
        study.save()


class Migration(migrations.Migration):

    dependencies = [
        ('emgapi', '0030_auto_20210414_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='superstudy',
            name='url_slug',
            field=models.SlugField(db_column='URL_SLUG', default=uuid.uuid4, max_length=100),
        ),
        migrations.RunPython(add_url_slug_to_super_studies, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='superstudy',
            name='url_slug',
            field=models.SlugField(db_column='URL_SLUG', max_length=100),
        ),
    ]