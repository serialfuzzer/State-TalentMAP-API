# Generated by Django 2.0.13 on 2020-05-22 13:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0008_auto_20191029_1941'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='mandatory_retirement_date',
        ),
    ]
