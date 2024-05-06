# Generated by Django 5.0.2 on 2024-04-13 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0056_supportteammessage_response'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('CREATED', 'Appointment created'), ('CANCELED', 'Appointment canceled'), ('APPOINTMENT_DONE', 'Appointment done'), ('DOCTOR_CANCELED', 'Doctor canceled appointment'), ('REMINDER', 'Appointment reminder'), ('NEWS', 'News added'), ('RESPONSE', 'Admin sent response')], max_length=20),
        ),
    ]