# Generated by Django 5.0.2 on 2024-03-13 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0024_alter_doctor_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='chats',
            field=models.ManyToManyField(blank=True, null=True, related_name='doctor_chats', to='Application.chat'),
        ),
    ]
