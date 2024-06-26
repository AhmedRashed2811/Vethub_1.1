# Generated by Django 5.0.2 on 2024-03-13 15:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0026_alter_doctor_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='rating',
            field=models.DecimalField(blank=True, decimal_places=1, default=0, max_digits=2, null=True, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='rating',
            field=models.DecimalField(decimal_places=1, max_digits=2, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(0)]),
        ),
    ]
