# Generated by Django 5.0.2 on 2024-04-20 03:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0067_doctor_appointment_minutes_alter_doctor_start_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctor',
            name='appointment_minutes',
        ),
    ]
