import typing

from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import CIEmailField, CITextField
from django.db import models

from .constants import FREQUENCY_CHOICES


class Type(models.Model):
    """
    The type
    """
    name = models.CharField(max_length=64)
    application = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)


class Person(models.Model):
    """
    The owner/contact person
    """
    name = models.CharField(max_length=255)
    email = models.EmailField()
    organisation = models.CharField(max_length=250, null=True, blank=True)


class Device(models.Model):
    """
    The iot device "thing"
    """
    reference = models.CharField(max_length=64)
    application = models.CharField(max_length=64)
    types = models.ManyToManyField(to='Type')
    categories = models.CharField(max_length=64, null=True, blank=True)
    installation_point = models.CharField(max_length=64, null=True)
    frequency = models.CharField(max_length=16, choices=FREQUENCY_CHOICES, null=True)
    permit = models.BooleanField(default=False, null=True, blank=True)
    in_use_since = models.DateField(null=True, blank=True)

    # Postal code, housenumber and location
    postal_code = models.CharField(max_length=6, null=True, blank=True)
    house_number = models.CharField(max_length=8, null=True, blank=True)
    geometrie = gis_models.PointField(name='geometrie', null=True, blank=True)

    # Owner and contact
    owner = models.ForeignKey(
        to='Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='owner')
    contact = models.ForeignKey(
        to='Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='contact')


# These models are loosely based on the data model from sensrnet, the intention
# is to migrate this data to the sensrnet system once we are able to host our
# own sensrnet node. For more information about the sensrnet data model see
# https://kadaster-labs.github.io/sensrnet-home/Model/


class Person2(models.Model):
    """
    The owner/contact person
    """
    # ContactDetails
    name = models.CharField(
        max_length=255,
        verbose_name="Naam (Voornaam [Tussenvoegsel] Achternaam)",
    )
    email = CIEmailField(unique=True, verbose_name="E-mail")
    telephone = models.CharField(max_length=15, verbose_name="Telefoon")

    # LegalEntity
    organisation = models.CharField(max_length=255, verbose_name="Naam organisatie/bedrijf")
    website = models.URLField(verbose_name="Website", blank=True, null=True)

    class Meta:
        verbose_name = 'Eigenaar'
        verbose_name_plural = 'Eigenaren'

    def __str__(self):
        return f'{self.email} ({self.name})'


class Type2(models.Model):
    name = CITextField(unique=True, verbose_name="Kies soort / type sensor")
    is_other = models.BooleanField(default=True, verbose_name="Anders, namelijk")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Type'
        verbose_name_plural = 'Types'


class Theme(models.Model):
    name = CITextField(unique=True, verbose_name="Thema")
    is_other = models.BooleanField(default=True, verbose_name="Anders, namelijk")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Thema'
        verbose_name_plural = 'Themas'


class LegalGround(models.Model):
    name = CITextField(unique=True, verbose_name="Wettelijke grondslag")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Wettelijke grondslag'
        verbose_name_plural = 'Wettelijke grondslagen'


def id_from_name(model: typing.Type[models.Model], name: str):
    """
    Get the id of the instance of model with the given name. Name should be a
    unique key, when the instance does not exist a DoesNotExist will be raised.
    """
    return model.objects.values_list('id', flat=True).filter(name=name).get()


class Region(models.Model):
    """
    A part of Amsterdam city, usually a "Stadsdeel" but users can also enter
    "other, namely..."
    """
    name = CITextField(unique=True, verbose_name="Gebied")
    is_other = models.BooleanField(default=True, verbose_name="Anders, namelijk")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Gebied'
        verbose_name_plural = 'Gebieden'


class ObservationGoal(models.Model):
    # name = models.CharField(max_length=255, verbose_name="Waarvoor meet u dat?")
    observation_goal = models.CharField(max_length=255, verbose_name="Waarvoor meet u dat?")
    privacy_declaration = models.URLField(verbose_name="Privacyverklaring", blank=False, null=False)
    # legal_ground = CITextField(blank=False, null=False, verbose_name="Wettelijke grondslag")
    legal_ground = models.ForeignKey(
        LegalGround,
        on_delete=models.PROTECT,
        verbose_name="Wettelijke grondslag",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.observation_goal

    class Meta:
        verbose_name = 'ObservationGoal'
        verbose_name_plural = 'ObservationGoals'


class Device2(models.Model):
    """
    The iot device "thing"
    """
    reference = models.CharField(max_length=64, verbose_name="Referentienummer")

    # LegalEntity
    owner = models.ForeignKey(
        Person2,
        on_delete=models.CASCADE,
        verbose_name="Eigenaar",
    )

    # Sensor
    type = models.ForeignKey(
        Type2,
        on_delete=models.PROTECT,
        verbose_name="Kies soort / type sensor",
    )

    # Location
    regions = models.ManyToManyField(
        Region,
        blank=True,
        verbose_name="In welk gebied bevindt zich de mobiele sensor?",
    )
    location = gis_models.PointField(
        name="location",
        null=True,
        blank=True,
        verbose_name="Vul de XYZ-coördinaten in",
    )
    location_description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Omschrijving van de locatie van de sensor",
    )

    # Datastream
    datastream = models.CharField(max_length=255, verbose_name="Wat meet de sensor?")
    themes = models.ManyToManyField(Theme, verbose_name="Thema")
    contains_pi_data = models.BooleanField(verbose_name="Worden er persoonsgegevens verwerkt?")

    # ObservationGoal
    # observation_goal = models.CharField(max_length=255, verbose_name="Waarvoor meet u dat?")
    observation_goals = models.ManyToManyField(
        ObservationGoal,
        verbose_name="ObservationGoal"
    )
    # legal_ground = models.ForeignKey(
    #     LegalGround,
    #     on_delete=models.PROTECT,
    #     verbose_name="Wettelijke grondslag",
    #     null=True,
    #     blank=True,
    # )
    active_until = models.DateField(null=True, verbose_name="Tot wanneer is de sensor actief?")

    def __str__(self):
        return self.reference

    class Meta:
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensoren'
        unique_together = 'reference', 'owner'
