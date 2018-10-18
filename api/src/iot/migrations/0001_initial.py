# Generated by Django 2.1.2 on 2018-10-15 11:21

import django.db.models.deletion
import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('street', models.CharField(max_length=255)),
                ('house_number', models.CharField(max_length=8)),
                ('house_number_addition', models.CharField(max_length=16)),
                ('postal_code', models.CharField(blank=True, max_length=10, null=True)),
                ('city', models.CharField(max_length=128)),
                ('municipality', models.CharField(blank=True, max_length=128, null=True)),
                ('country', django_countries.fields.CountryField(max_length=2)),
            ],
            options={
                'verbose_name': 'address',
                'verbose_name_plural': 'addresses',
            },
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('reference', models.CharField(max_length=64)),
                ('application', models.CharField(max_length=64)),
                ('longitude', models.FloatField()),
                ('latitude', models.FloatField()),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              to='iot.Address')),
            ],
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('application', models.CharField(max_length=64)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='device',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iot.Owner'),
        ),
        migrations.AddField(
            model_name='device',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iot.Type'),
        ),
    ]
