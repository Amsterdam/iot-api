from django.db import models
from django.utils.translation import ugettext as _
from django_countries.fields import CountryField

from iot.constants import FREQUENCY_CHOICES


class Address(models.Model):
    """
    Address model, representing an actual address
    """
    street = models.CharField(
        max_length=255,
    )

    house_number = models.CharField(
        max_length=8,
    )

    house_number_addition = models.CharField(
        max_length=16,
    )

    postal_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
    )

    city = models.CharField(
        max_length=128,
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
    name = models.CharField(
        max_length=255,
    )

    email = models.EmailField()


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
    type = models.ForeignKey(
        to='Type',
        on_delete=models.SET_NULL,
        null=True,
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
        blank=True
    )
    in_use_since = models.DateField(
        null=True,
    )

    # Location
    address = models.ForeignKey(
        to='Address',
        on_delete=models.CASCADE,
    )
    longitude = models.FloatField()
    latitude = models.FloatField()

    # Owner and contact
    organisation = models.CharField(
        max_length=250,
    )
    owner = models.ForeignKey(
        to='Person',
        on_delete=models.CASCADE,
        null=True,
        related_name='owner',
    )
    contact = models.ForeignKey(
        to='Person',
        on_delete=models.SET_NULL,
        null=True,
        related_name='contact',
    )
