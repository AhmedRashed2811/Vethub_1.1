# Generated by Django 5.0.2 on 2024-04-14 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0058_supportteammessage_answered'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='city',
            field=models.CharField(max_length=150),
        ),
    ]