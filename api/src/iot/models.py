from django.db import models
from django.utils.translation import ugettext as _
from django_countries.fields import CountryField


class Address(models.Model):
    """
    Address model, representing and actual address
    """
    street = models.CharField(
        max_length=255
    )

    house_number = models.CharField(
        max_length=8
    )

    house_number_addition = models.CharField(
        max_length=16
    )

    postal_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
    )

    city = models.CharField(
        max_length=128
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
        max_length=64
    )

    application = models.CharField(
        max_length=64
    )

    description = models.TextField()


class Owner(models.Model):
    """
    The owner of an iot device
    """
    name = models.CharField(
        max_length=64
    )

    email = models.EmailField()


class Device(models.Model):
    """
    The iot device
    """
    reference = models.CharField(
        max_length=64
    )

    application = models.CharField(
        max_length=64
    )

    longitude = models.FloatField()

    latitude = models.FloatField()

    owner = models.ForeignKey(
        to='Owner',
        on_delete=models.CASCADE,
    )

    address = models.ForeignKey(
        to='Address',
        on_delete=models.CASCADE,
    )

    type = models.ForeignKey(
        to='Type',
        on_delete=models.CASCADE,
    )
