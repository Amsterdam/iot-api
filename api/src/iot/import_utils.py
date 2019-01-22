from collections import namedtuple

import requests
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from iot.constants import (CATEGORY_BEACON, CATEGORY_CAMERA, CATEGORY_SENSOR,
                           CATEGORY_SMART_TRAFFIC_INFORMATION)
from iot.models import Device, Person, Type
from iot.settings import settings

CSV_MAPPING = {
    'sensor': CATEGORY_SENSOR,
    'baken': CATEGORY_BEACON,
    'slimme verkeersinformatie ': CATEGORY_SMART_TRAFFIC_INFORMATION,
    'camera': CATEGORY_CAMERA,
}


class PostcodeSearchException(Exception):
    pass


def get_center_coordinates(postcode: str) -> Point:
    response = requests.get('{}/?q={}'.format(settings.ATLAS_POSTCODE_SEARCH, postcode))
    data = response.json()
    if not data['results'] or 'centroid' not in data['results'][0]:
        raise PostcodeSearchException()
    return Point(data['results'][0]['centroid'][1], data['results'][0]['centroid'][0])


CsvRow = namedtuple('CsvRow', ['name', 'categories', 'types', 'x', 'y', 'long', 'lat',
                               'postalcode', 'housenumber', 'owner_name', 'owner_organisation',
                               'owner_email', 'contact_name', 'contact_organisation',
                               'contact_email', ])


class CsvRowValidationException(Exception):
    pass


def import_row(csv_row: CsvRow) -> None:
    if not validate_row(csv_row=csv_row):
        raise CsvRowValidationException('Invalid row')

    if csv_row.types:
        device_type, _ = Type.objects.update_or_create(
            name=csv_row.types,
            defaults={
                'application': csv_row.types
            })
    else:
        device_type = None

    owner, _ = Person.objects.get_or_create(
        email=csv_row.owner_email,
        defaults={
            'name': csv_row.owner_name,
            'organisation': csv_row.owner_organisation,
        }
    )
    contact, _ = Person.objects.get_or_create(
        email=csv_row.contact_email,
        defaults={
            'name': csv_row.contact_name,
            'organisation': csv_row.contact_organisation,
        }
    )

    device_data = {
        'reference': csv_row.name,
        'application': csv_row.categories,
        'categories': CSV_MAPPING.get(csv_row.categories.lower(), None),
        'owner': owner,
        'contact': contact,
    }

    if csv_row.x and csv_row.y:
        # X and Y
        point = Point(x=float(csv_row.x), y=float(csv_row.y), srid=28992)
        point.transform(ct=4326)
    elif csv_row.lat and csv_row.long:
        # Lat and Long
        point = Point(x=float(csv_row.long), y=float(csv_row.lat), srid=4326)
        device_data.update({'geometrie': point})
    else:
        # Need to calculate the long lat from the postcode
        point = get_center_coordinates(csv_row.postalcode)

    device_data.update({'geometrie': point})
    device = Device.objects.create(**device_data)
    if device_type:
        device.types.set((device_type.pk, ))
        device.save()


def _validate_email(email: str) -> bool:
    try:
        validate_email(email)
    except ValidationError:
        return False
    return True


def validate_row(csv_row: CsvRow) -> bool:
    return not any([
        not csv_row.owner_name,
        not csv_row.contact_name,
        not _validate_email(csv_row.owner_email),
        not _validate_email(csv_row.contact_email),
        not any([csv_row.x, csv_row.y, csv_row.long, csv_row.lat, csv_row.postalcode])
    ])
