# Generated by Django 5.0.2 on 2024-04-14 21:42

import Application.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0059_alter_doctor_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='image',
            field=models.ImageField(upload_to=Application.models.PathAndRename('news')),
        ),
    ]
