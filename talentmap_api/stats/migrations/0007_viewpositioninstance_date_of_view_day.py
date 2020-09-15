# Generated by Django 2.0.13 on 2020-09-10 17:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0006_viewpositioninstance'),
    ]

    operations = [
        migrations.AddField(
            model_name='viewpositioninstance',
            name='date_of_view_day',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
