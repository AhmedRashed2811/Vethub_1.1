# Generated by Django 5.0.2 on 2024-04-09 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0048_alter_doctor_certifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='appointments_count',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
