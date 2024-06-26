# Generated by Django 5.0.2 on 2024-04-20 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0064_appointment_reported'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='day_off',
            field=models.CharField(choices=[('Saturday', 'Saturday'), ('Sunday', 'Sunday'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday')], default='None', max_length=10),
        ),
        migrations.AddField(
            model_name='doctor',
            name='finish_time',
            field=models.CharField(default='11:30 pm', max_length=10),
        ),
        migrations.AddField(
            model_name='doctor',
            name='start_time',
            field=models.CharField(default='10:00 am', max_length=10),
        ),
    ]
