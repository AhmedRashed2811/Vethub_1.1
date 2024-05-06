# Generated by Django 5.0.2 on 2024-03-01 13:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0014_customer_chats_doctor_chats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Application.customer'),
        ),
        migrations.AlterField(
            model_name='chat',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Application.doctor'),
        ),
    ]