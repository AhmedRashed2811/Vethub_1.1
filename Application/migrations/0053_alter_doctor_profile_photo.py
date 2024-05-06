# Generated by Django 5.0.2 on 2024-04-11 00:06

import Application.models
import django_resized.forms
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0052_alter_doctor_certifications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='profile_photo',
            field=django_resized.forms.ResizedImageField(crop=None, force_format=None, keep_meta=True, quality=80, scale=None, size=[500, 500], upload_to=Application.models.PathAndRename('Profile_Photos')),
        ),
    ]
