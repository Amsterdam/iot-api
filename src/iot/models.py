import typing

from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import ArrayField, CIEmailField, CITextField
from django.db import models

# These models are loosely based on the data model from sensrnet, the intention
# is to migrate this data to the sensrnet system once we are able to host our
# own sensrnet node. For more information about the sensrnet data model see
# https://kadaster-labs.github.io/sensrnet-home/Model/


class Person(models.Model):
    """
    The owner/contact person
    """

    # ContactDetails
    name = models.CharField(
        max_length=255,
        verbose_name="Naam (Voornaam [Tussenvoegsel] Achternaam)",
    )
    email = CIEmailField(verbose_name="E-mail")
    telephone = models.CharField(max_length=15, verbose_name="Telefoon")

    # LegalEntity
    organisation = models.CharField(
        max_length=255, verbose_name="Naam organisatie/bedrijf"
    )
    website = models.TextField(verbose_name="Website", blank=True, null=True)

    class Meta:
        verbose_name = 'Eigenaar'
        verbose_name_plural = 'Eigenaren'
        unique_together = [['email', 'organisation']]

    def __str__(self):
        return f'{self.email} ({self.name})'


class Type(models.Model):
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
    observation_goal = models.CharField(
        max_length=255, verbose_name="Waarvoor meet u dat?", blank=True, null=True
    )
    privacy_declaration = models.URLField(
        verbose_name="Privacyverklaring", blank=True, null=True
    )
    legal_ground = models.ForeignKey(
        LegalGround,
        on_delete=models.PROTECT,
        verbose_name="Wettelijke grondslag",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.observation_goal} - {self.legal_ground}'

    class Meta:
        verbose_name = 'ObservationGoal'
        verbose_name_plural = 'ObservationGoals'


class Project(models.Model):
    """represents a list of paths to the projects that belong to a device."""

    path = ArrayField(
        models.CharField(
            max_length=255, verbose_name="Organisation name", blank=False, null=False
        )
    )

    def __str__(self):
        return f'{self.path}'

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'


class Device(models.Model):
    """
    The iot device "thing"
    """

    reference = models.CharField(max_length=64, verbose_name="Referentienummer")

    # LegalEntity
    owner = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        verbose_name="Eigenaar",
    )

    # Sensor
    type = models.ForeignKey(
        Type,
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
    contains_pi_data = models.BooleanField(
        verbose_name="Worden er persoonsgegevens verwerkt?"
    )

    # ObservationGoal
    observation_goals = models.ManyToManyField(
        ObservationGoal, verbose_name="ObservationGoal"
    )

    projects = models.ManyToManyField(Project, verbose_name="Projects")

    active_until = models.DateField(
        null=True, verbose_name="Tot wanneer is de sensor actief?"
    )

    def __str__(self):
        return self.reference

    class Meta:
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensoren'
        unique_together = 'reference', 'owner'
