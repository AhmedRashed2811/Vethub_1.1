# Generated by Django 5.0.2 on 2024-04-10 23:11

import Application.models
import django_resized.forms
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0051_alter_doctor_certifications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='certifications',
            field=django_resized.forms.ResizedImageField(crop=None, force_format=None, keep_meta=True, quality=80, scale=None, size=[800, 600], upload_to=Application.models.PathAndRename('Certifications')),
        ),
    ]
