# Generated by Django 3.2.13 on 2022-07-04 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iot', '0013_email_organisation_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person2',
            name='website',
            field=models.TextField(blank=True, null=True, verbose_name='Website'),
        ),
    ]
