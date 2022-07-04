# Generated by Django 3.2.13 on 2022-07-04 09:52

import django.contrib.postgres.fields.citext
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iot', '0012_new_model_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person2',
            name='email',
            field=django.contrib.postgres.fields.citext.CIEmailField(max_length=254, verbose_name='E-mail'),
        ),
        migrations.AlterUniqueTogether(
            name='person2',
            unique_together={('email', 'organisation')},
        ),
    ]
