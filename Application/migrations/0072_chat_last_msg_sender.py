# Generated by Django 5.0.2 on 2024-04-22 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0071_chat_last_msg_seen'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='last_msg_sender',
            field=models.CharField(choices=[('Customer', 'Customer'), ('Doctor', 'Doctor')], default='Customer', max_length=10),
        ),
    ]
