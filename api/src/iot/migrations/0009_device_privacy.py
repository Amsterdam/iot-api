# Generated by Django 2.2.8 on 2020-02-13 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iot', '0008_auto_20191119_0907'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='privacy',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
