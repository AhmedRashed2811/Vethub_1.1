# Generated by Django 5.0.2 on 2024-04-13 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0055_alter_doctor_profile_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportteammessage',
            name='response',
            field=models.TextField(blank=True, null=True),
        ),
    ]