# Generated by Django 3.2.16 on 2022-11-29 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iot', '0017_devicejson'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='organisation',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Naam organisatie/bedrijf'),
        ),
        migrations.AlterField(
            model_name='person',
            name='website',
            field=models.URLField(blank=True, null=True, verbose_name='Website'),
        ),
    ]