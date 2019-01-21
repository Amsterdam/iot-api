from django.contrib.gis.db import models as gis_models
from django.db import models
from multiselectfield import MultiSelectField

from iot.constants import CATEGORY_CHOICES, FREQUENCY_CHOICES


class Type(models.Model):
    """
    The type
    """
    name = models.CharField(
        max_length=64,
    )

    application = models.CharField(
        max_length=64,
    )

    description = models.TextField()


class Person(models.Model):
    """
    The owner/contact person
    """
    name = models.CharField(
        max_length=255,
    )

    email = models.EmailField()

    organisation = models.CharField(
        max_length=250,
        null=True,
        blank=True,
    )


class Device(models.Model):
    """
    The iot device "thing"
    """
    reference = models.CharField(
        max_length=64,
    )
    application = models.CharField(
        max_length=64,
    )
    types = models.ManyToManyField(
        to='Type',
    )
    categories = MultiSelectField(
        choices=CATEGORY_CHOICES,
        max_length=64,
        max_choices=6,
        null=True,
        blank=True,
    )
    installation_point = models.CharField(
        max_length=64,
        null=True,
    )
    frequency = models.CharField(
        max_length=16,
        choices=FREQUENCY_CHOICES,
        null=True,
    )
    permit = models.BooleanField(
        default=False,
        null=True,
        blank=True,
    )
    in_use_since = models.DateField(
        null=True,
        blank=True,
    )

    # Postal code, housenumber and location
    postal_code = models.CharField(
        max_length=6,
        null=True,
        blank=True,
    )
    house_number = models.CharField(
        max_length=8,
        null=True,
        blank=True,
    )
    geometrie = gis_models.PointField(name='geometrie', null=True, blank=True)

    # Owner and contact
    owner = models.ForeignKey(
        to='Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owner',
    )
    contact = models.ForeignKey(
        to='Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact',
    )
