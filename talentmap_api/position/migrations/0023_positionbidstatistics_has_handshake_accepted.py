# Generated by Django 2.0.4 on 2019-03-11 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('position', '0022_positionbidstatistics_has_handshake_offered'),
    ]

    operations = [
        migrations.AddField(
            model_name='positionbidstatistics',
            name='has_handshake_accepted',
            field=models.BooleanField(default=False),
        ),
    ]
