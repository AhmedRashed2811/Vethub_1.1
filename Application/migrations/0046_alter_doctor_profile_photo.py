# Generated by Django 5.0.2 on 2024-04-07 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0045_alter_doctor_profile_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='profile_photo',
            field=models.ImageField(upload_to=''),
        ),
    ]