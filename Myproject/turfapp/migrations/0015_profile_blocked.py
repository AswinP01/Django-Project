# Generated by Django 5.0.6 on 2024-07-22 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('turfapp', '0014_alter_booking_end_time_alter_booking_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='blocked',
            field=models.BooleanField(default=False),
        ),
    ]