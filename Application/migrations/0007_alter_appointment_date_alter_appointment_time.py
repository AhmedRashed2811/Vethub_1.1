# Generated by Django 5.0.2 on 2024-02-29 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0006_appointment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='time',
            field=models.TextField(),
        ),
    ]
