from django.db import models
from django.utils.translation import ugettext as _
from django_countries.fields import CountryField
from multiselectfield import MultiSelectField

from iot.constants import CATEGORY_CHOICES, FREQUENCY_CHOICES


class Address(models.Model):
    """
    Address model, representing an actual address
    """
    street = models.CharField(
        max_length=255,
    )

    house_number = models.CharField(
        max_length=8,
        null=True,
        blank=True,
    )

    house_number_addition = models.CharField(
        max_length=16,
        null=True,
        blank=True,
    )

    postal_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
    )

    city = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )

    municipality = models.CharField(
        max_length=128,
        blank=True,
        null=True,
    )

    country = CountryField()

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')


class Location(models.Model):
    """
    The location of the device
    """
    longitude = models.FloatField()
    latitude = models.FloatField()


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
        null=True,
        blank=True,
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

    # Address / Location
    address = models.ForeignKey(
        to='Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        to='Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

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
