# Generated by Django 5.0.2 on 2024-03-11 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0022_news'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
