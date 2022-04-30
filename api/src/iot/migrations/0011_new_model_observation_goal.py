# Generated by Django 3.2.9 on 2022-03-30 15:09

import django.contrib.postgres.fields.citext
from django.db import migrations, models


def make_many_observationgoals(apps, schema_editor):
    """
        Adds the Device2 object in device2.observation_goals to the
        many-to-many relationship in Device2.observationgoals
    """
    Device2 = apps.get_model('iot', 'Device2')
    ObservationGoal = apps.get_model('iot', 'ObservationGoal')

    for device2 in Device2.objects.all():
        result = ObservationGoal.objects.get_or_create(
            observation_goal=device2.observation_goal,
            privacy_declaration=device2.privacy_declaration,
            legal_ground=device2.legal_ground)[0]
        device2.observation_goals.add(result)


def reverse_many_observationgoals(apps, schema_editor):
    """
    Reverse the data from the ObservationGoals to Device2.
    """
    Device2 = apps.get_model('iot', 'Device2')

    for device2 in Device2.objects.all():
        observation_goals = device2.observation_goals.values_list(
            'observation_goal',
            'privacy_declaration',
            'legal_ground_id'
        )
        # because the list of observation_goals has one element when the change took place, 
        # I use the first element (index 0) only from it.
        device2.observation_goal = observation_goals[0][0]
        device2.privacy_declaration = observation_goals[0][1]
        device2.legal_ground_id = observation_goals[0][2]
        device2.save()


class Migration(migrations.Migration):

    dependencies = [
        ('iot', '0010_theme_is_other'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObservationGoal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observation_goal', models.CharField(max_length=255, verbose_name='Waarvoor meet u dat?')),
                ('privacy_declaration', models.URLField(blank=True, null=True, verbose_name='Privacyverklaring')),
                ('legal_ground', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='iot.legalground', verbose_name='Wettelijke grondslag')),
            ],
            options={
                'verbose_name': 'ObservationGoal',
                'verbose_name_plural': 'ObservationGoals',
            },
        ),
        migrations.AddField(
            model_name='device2',
            name='observation_goals',
            field=models.ManyToManyField(to='iot.ObservationGoal', verbose_name='ObservationGoal'),
        ),
        migrations.RunPython(
            make_many_observationgoals, 
            reverse_code=reverse_many_observationgoals
        ),
        migrations.RemoveField(
            model_name='device2',
            name='legal_ground',
        ),
        migrations.RemoveField(
            model_name='device2',
            name='privacy_declaration',
        ),
        migrations.RemoveField(
            model_name='device2',
            name='observation_goal',
        ),
    ]
