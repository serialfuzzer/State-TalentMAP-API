# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-28 18:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0001_initial'),
        ('bidding', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_string_representation', models.TextField(blank=True, help_text='The string representation of this object', null=True)),
                ('status', models.TextField(choices=[('pending', 'pending'), ('assigned', 'assigned'), ('active', 'active'), ('completed', 'completed'), ('curtailed', 'curtailed')], default='pending')),
                ('curtailment_reason', models.TextField(choices=[('medical', 'medical'), ('clearance', 'clearance'), ('service_need', 'service_need'), ('compassionate', 'compassionate'), ('other', 'other')], null=True)),
                ('create_date', models.DateField(auto_now_add=True, help_text='The date the assignment was created')),
                ('start_date', models.DateField(help_text='The date the assignment started', null=True)),
                ('estimated_end_date', models.DateField(help_text='The estimated end date based upon tour of duty', null=True)),
                ('end_date', models.DateField(help_text='The date this position was completed or curtailed', null=True)),
                ('service_duration', models.IntegerField(help_text='The duration of a completed assignment in months', null=True)),
                ('update_date', models.DateField(auto_now=True)),
            ],
            options={
                'ordering': ['update_date'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CapsuleDescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_string_representation', models.TextField(blank=True, help_text='The string representation of this object', null=True)),
                ('content', models.TextField(null=True)),
                ('point_of_contact', models.TextField(null=True)),
                ('website', models.TextField(null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('_pos_seq_num', models.TextField(null=True)),
            ],
            options={
                'ordering': ['date_updated'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Classification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_string_representation', models.TextField(blank=True, help_text='The string representation of this object', null=True)),
                ('code', models.TextField(db_index=True, help_text='The classification code', unique=True)),
                ('description', models.TextField(help_text='Text description of the classification')),
            ],
            options={
                'ordering': ['code'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_string_representation', models.TextField(blank=True, help_text='The string representation of this object', null=True)),
                ('code', models.TextField(db_index=True, unique=True)),
                ('rank', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['rank'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_string_representation', models.TextField(blank=True, help_text='The string representation of this object', null=True)),
                ('position_number', models.TextField(help_text='The position number', null=True)),
                ('title', models.TextField(help_text='The position title', null=True)),
                ('is_overseas', models.BooleanField(default=False, help_text='Flag designating whether the position is overseas')),
                ('create_date', models.DateField(help_text='The creation date of the position', null=True)),
                ('update_date', models.DateField(help_text='The update date of this position', null=True)),
                ('effective_date', models.DateField(help_text='The effective date of this position', null=True)),
                ('_seq_num', models.TextField(null=True)),
                ('_title_code', models.TextField(null=True)),
                ('_org_code', models.TextField(null=True)),
                ('_bureau_code', models.TextField(null=True)),
                ('_skill_code', models.TextField(null=True)),
                ('_staff_ptrn_skill_code', models.TextField(null=True)),
                ('_pay_plan_code', models.TextField(null=True)),
                ('_status_code', models.TextField(null=True)),
                ('_service_type_code', models.TextField(null=True)),
                ('_grade_code', models.TextField(null=True)),
                ('_post_code', models.TextField(null=True)),
                ('_location_code', models.TextField(null=True)),
                ('_create_id', models.TextField(null=True)),
                ('_update_id', models.TextField(null=True)),
                ('_jobcode_code', models.TextField(null=True)),
                ('_occ_series_code', models.TextField(null=True)),
                ('bureau', models.ForeignKey(help_text='The bureau for this position', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bureau_positions', to='organization.Organization')),
                ('classifications', models.ManyToManyField(related_name='positions', to='position.Classification')),
                ('current_assignment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_for_position', to='position.Assignment')),
                ('description', models.OneToOneField(help_text='A plain text description of the position', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='position', to='position.CapsuleDescription')),
                ('grade', models.ForeignKey(help_text='The job grade for this position', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='position.Grade')),
                ('organization', models.ForeignKey(help_text='The organization for this position', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='organization_positions', to='organization.Organization')),
                ('post', models.ForeignKey(help_text='The position post', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='organization.Post')),
            ],
            options={
                'ordering': ['position_number'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PositionBidStatistics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_string_representation', models.TextField(blank=True, help_text='The string representation of this object', null=True)),
                ('total_bids', models.IntegerField(default=0)),
                ('in_grade', models.IntegerField(default=0)),
                ('at_skill', models.IntegerField(default=0)),
                ('in_grade_at_skill', models.IntegerField(default=0)),
                ('bidcycle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='position_bid_statistics', to='bidding.BidCycle')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bid_statistics', to='position.Position')),
            ],
            options={
                'ordering': ['bidcycle__cycle_start_date'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_string_representation', models.TextField(blank=True, help_text='The string representation of this object', null=True)),
                ('code', models.TextField(db_index=True, help_text='4 character string code representation of the job skill', unique=True)),
                ('description', models.TextField(help_text='Text description of the job skill')),
            ],
            options={
                'ordering': ['code'],
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='position',
            name='skill',
            field=models.ForeignKey(help_text='The job skill for this position', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='position.Skill'),
        ),
        migrations.AddField(
            model_name='position',
            name='tour_of_duty',
            field=models.ForeignKey(help_text='The tour of duty of the post', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='organization.TourOfDuty'),
        ),
    ]
