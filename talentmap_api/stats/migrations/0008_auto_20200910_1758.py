# Generated by Django 2.0.13 on 2020-09-10 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0007_viewpositioninstance_date_of_view_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='viewpositioninstance',
            name='date_of_view_day',
            field=models.TextField(),
        ),
    ]
