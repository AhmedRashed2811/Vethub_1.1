# Generated by Django 5.0.2 on 2024-03-01 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0013_chat'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='chats',
            field=models.ManyToManyField(related_name='customer_chats', to='Application.chat'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='chats',
            field=models.ManyToManyField(related_name='doctor_chats', to='Application.chat'),
        ),
    ]
