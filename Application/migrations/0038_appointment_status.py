# Generated by Django 5.0.2 on 2024-03-16 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0037_remove_appointment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('On-Going', 'On-Going'), ('Done', 'Done')], default='Pending', max_length=10),
        ),
    ]
