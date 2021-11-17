# Generated by Django 3.2.9 on 2021-11-21 11:33

import logging

import django.contrib.gis.db.models.fields
from django.db import migrations, models

import django.contrib.postgres.fields.citext
from django.contrib.postgres.operations import CITextExtension
from django.db import migrations, models, ProgrammingError
import django.db.models.deletion


logger = logging.getLogger(__name__)


class TryCITextExtension(CITextExtension):
    '''
    Create citext extension on postgres, but handle insufficient privilege exception.
    This will run locally and will not fail on acceptance on production where the django account does not have sufficient privileges to install the extension.
    On acceptance and production this extension has already been installed.
    '''
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        try:
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        except ProgrammingError:
            logger.exception(
                "Failed to create citext extension because of missing permissions"
            )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        try:
            super().database_backwards(app_label, schema_editor, from_state, to_state)
        except ProgrammingError:
            logger.exception(
                "Failed to remove citext extension because of missing permissions"
            )


def load_initial_data(apps, schema_editor):
    Theme = apps.get_model('iot', 'Theme')
    Theme.objects.bulk_create([
        Theme(name="Energie"),
        Theme(name="Landbouw, visserij, voedselkwaliteit"),
        Theme(name="Transport"),
        Theme(name="Afval"),
        Theme(name="Bodem"),
        Theme(name="Geluid"),
        Theme(name="Klimaatverandering"),
        Theme(name="Lucht"),
        Theme(name="Natuur- en landschapsbeheer"),
        Theme(name="Water"),
        Theme(name="Veiligheid"),
        Theme(name="Ruimtelijke ordening"),
        Theme(name="Waterbeheer"),
        Theme(name="Luchtvaart"),
        Theme(name="Openbaar vervoer"),
        Theme(name="Rail- en wegverkeer"),
        Theme(name="Scheepvaart"),
        Theme(name="Bouwen en verbouwen"),
        Theme(name="Woningmarkt"),
        Theme(name="Gezondheidsrisico's"),
    ])

    LegalGround = apps.get_model('iot', 'LegalGround')
    LegalGround.objects.bulk_create([
        LegalGround(name='Publieke taak'),
        LegalGround(name='Gerechtvaardigd belang'),
        LegalGround(name='Wettelijke verplichting'),
        LegalGround(name='Toestemming betrokkene(n)'),
        LegalGround(name='Uitvoering overeenkomst met betrokkene(n)'),
        LegalGround(name='Bescherming vitale belangen betrokkene(n) of van een andere natuurlijke persoon)'),
    ])

    Type2 = apps.get_model('iot', 'Type2')
    Type2.objects.bulk_create([
        Type2(name='Optische / camera sensor', is_other=False),
        Type2(name='Geluidsensor', is_other=False),
        Type2(name='Klimaatsensor', is_other=False),
        Type2(name='Chemiesensor', is_other=False),
        Type2(name='Electriciteitssensor', is_other=False),
        Type2(name='Vloeistof- en gasstroomsensor', is_other=False),
        Type2(name='Positie- of verplaatsingsensor', is_other=False),
        Type2(name='Druksensor', is_other=False),
        Type2(name='Dichtheidssensor', is_other=False),
        Type2(name='Temperatuursensor', is_other=False),
        Type2(name='Aanwezigheid of nabijheidsensor', is_other=False),
    ])

    Region = apps.get_model('iot', 'Region')
    Region.objects.bulk_create([
        Region(name='Geheel Amsterdam', is_other=False),
        Region(name='Stadsdeel Centrum', is_other=False),
        Region(name='Stadsdeel Nieuw - West', is_other=False),
        Region(name='Stadsdeel Noord', is_other=False),
        Region(name='Stadsdeel Oost', is_other=False),
        Region(name='Stadsdeel West', is_other=False),
        Region(name='Stadsdeel Zuid', is_other=False),
        Region(name='Stadsdeel Zuidoost', is_other=False),
        Region(name='Weesp', is_other=False),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('iot', '0008_auto_20191119_0907'),
    ]

    operations = [
        TryCITextExtension(),
        migrations.CreateModel(
            name='LegalGround',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Wettelijke grondslag')),
            ],
            options={
                'verbose_name': 'Wettelijke grondslag',
                'verbose_name_plural': 'Wettelijke grondslagen',
            },
        ),
        migrations.CreateModel(
            name='Person2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Naam (Voornaam [Tussenvoegsel] Achternaam)')),
                ('email', django.contrib.postgres.fields.citext.CIEmailField(max_length=254, unique=True, verbose_name='E-mail')),
                ('telephone', models.CharField(max_length=15, verbose_name='Telefoon')),
                ('organisation', models.CharField(max_length=255, verbose_name='Naam organisatie/bedrijf')),
                ('website', models.URLField(verbose_name='Website')),
            ],
            options={
                'verbose_name': 'Eigenaar',
                'verbose_name_plural': 'Eigenaren',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Gebied')),
                ('is_other', models.BooleanField(default=True, verbose_name='Anders, namelijk')),
            ],
            options={
                'verbose_name': 'Gebied',
                'verbose_name_plural': 'Gebieden',
            },
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Thema')),
            ],
            options={
                'verbose_name': 'Thema',
                'verbose_name_plural': 'Themas',
            },
        ),
        migrations.CreateModel(
            name='Type2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Kies soort / type sensor')),
                ('is_other', models.BooleanField(default=True, verbose_name='Anders, namelijk')),
            ],
            options={
                'verbose_name': 'Type',
                'verbose_name_plural': 'Types',
            },
        ),
        migrations.CreateModel(
            name='Device2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=64, verbose_name='Referentienummer')),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326, verbose_name='Vul de XYZ-coördinaten in')),
                ('location_description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Omschrijving van de locatie van de sensor')),
                ('datastream', models.CharField(max_length=255, verbose_name='Wat meet de sensor?')),
                ('contains_pi_data', models.BooleanField(verbose_name='Worden er persoonsgegevens verwerkt?')),
                ('observation_goal', models.CharField(max_length=255, verbose_name='Waarvoor meet u dat?')),
                ('privacy_declaration', models.URLField(verbose_name='Privacyverklaring', blank=True, null=True)),
                ('active_until', models.DateField(null=True, verbose_name='Tot wanneer is de sensor actief?')),
                ('legal_ground', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='iot.legalground', verbose_name='Wettelijke grondslag')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iot.person2', verbose_name='Eigenaar')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='iot.region', verbose_name='In welk gebied bevindt zich de mobiele sensor?')),
                ('themes', models.ManyToManyField(to='iot.Theme', verbose_name='Thema')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='iot.type2', verbose_name='Kies soort / type sensor')),
            ],
            options={
                'verbose_name': 'Sensor',
                'verbose_name_plural': 'Sensoren',
                'unique_together': {('reference', 'owner')},
            },
        ),
        # reverse not needed, since when reversing this the models will be
        # deleted anyway
        migrations.RunPython(load_initial_data),
    ]
