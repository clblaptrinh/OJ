# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-31 18:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def move_current_contest_to_profile(apps, schema_editor):
    ContestProfile = apps.get_model('judge', 'ContestProfile')
    db_alias = schema_editor.connection.alias
    for cp in ContestProfile.objects.using(db_alias).filter(current__is_null=False).select_related('user'):
        cp.user.current_contest_id = cp.current_id
        cp.user.save()


def move_current_contest_to_contest_profile(apps, schema_editor):
    ContestProfile = apps.get_model('judge', 'ContestProfile')
    Profile = apps.get_model('judge', 'Profile')
    db_alias = schema_editor.connection.alias
    for profile in Profile.objects.using(db_alias).filter(current_contest__is_null=None):
        cp = ContestProfile.objects.get_or_create(user=profile)
        cp.current_id = profile.current_contest_id
        cp.save()


def contest_participation_to_profile(apps, schema_editor):
    ContestParticipation = apps.get_model('judge', 'ContestParticipation')
    db_alias = schema_editor.connection.alias
    for cp in ContestParticipation.objects.using(db_alias).select_related('profile'):
        cp.user_id = cp.profile.user_id
        cp.save()


def contest_participation_to_contest_profile(apps, schema_editor):
    ContestParticipation = apps.get_model('judge', 'ContestParticipation')
    ContestProfile = apps.get_model('judge', 'ContestProfile')
    db_alias = schema_editor.connection.alias
    for cp in ContestParticipation.objects.using(db_alias).select_related('profile'):
        cp.profile = ContestProfile.objects.get_or_create(user_id=cp.user_id)
        cp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0029_problem_translation'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='current_contest',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='judge.ContestParticipation', verbose_name='Current contest'),
        ),
        migrations.RunPython(move_current_contest_to_profile, move_current_contest_to_contest_profile),
        migrations.AddField(
            model_name='contestparticipation',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contest_history', to='judge.Profile', verbose_name='user'),
            preserve_default=False,
        ),
        migrations.RunPython(contest_participation_to_profile, contest_participation_to_contest_profile),
        migrations.RemoveField(
            model_name='contestparticipation',
            name='profile',
        ),
        migrations.DeleteModel(name='contestprofile'),
    ]
