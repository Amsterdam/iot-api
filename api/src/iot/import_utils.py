import contextlib
import dataclasses
import datetime
import re
from itertools import islice, zip_longest
from typing import Generator, Union

import requests
from django.conf import settings
from django.contrib.gis.geos import Point
from openpyxl import Workbook
from openpyxl.cell import Cell
from typing_extensions import Literal

from iot import models


@dataclasses.dataclass
class PostcodeSearchException(ValueError):
    postcode: str
    house_number: int

    def __str__(self):
        return f"Ongeldige postcode {self.postcode} of huisnummer {self.house_number}"


def get_postcode_url(postcode: str) -> str:
    normalized = postcode.replace(' ', '')
    return f'{settings.ATLAS_POSTCODE_SEARCH}/?q={normalized}'


def get_address_url(street: str, house_number: int) -> str:
    normalized = f'{street.lower()} {house_number}'
    return f'{settings.ATLAS_ADDRESS_SEARCH}/?q={normalized}'


def get_center_coordinates(postcode: str, house_number: int) -> Point:
    """
    :return: The centroid longitude and latitude coordinates for a postcode and
             the house number on that street.
    """
    url = get_postcode_url(postcode)
    data = requests.get(url).json()

    if not data or not data.get('results') or 'naam' not in data['results'][0]:
        raise PostcodeSearchException(postcode, house_number)

    url = get_address_url(data['results'][0]['naam'], house_number)

    while url is not None:

        data = requests.get(url).json()
        if not data.get('results'):
            break

        # ensure that we get the actual house number we were looking for, it may
        # be that this number does not exist on the street. The search is fuzzy
        # so we will most likely get a result, but it might not be the result we
        # want
        postcode_normalized = postcode.replace(' ', '')
        for result in data['results']:

            if 'centroid' not in result:
                raise PostcodeSearchException(postcode, house_number)

            if result.get('postcode') == postcode_normalized and \
                    result.get('huisnummer') == house_number:
                centroid = result['centroid']
                return Point(centroid[0], centroid[1])

        # not found in this page, try next one
        url = data.get('_links')['next']['href']

    # If we got here it is because we didn't find a result with the correct
    # postcode and house number, so it seems this house number does not exist
    # for the given postcode.
    raise PostcodeSearchException(postcode, house_number)


@dataclasses.dataclass
class PersonData:
    organisation: str
    email: str
    telephone: str
    website: str
    first_name: str
    last_name_affix: str
    last_name: str


@dataclasses.dataclass
class LatLong:
    latitude: Union[float, str]
    longitude: Union[float, str]


@dataclasses.dataclass
class PostcodeHouseNumber:
    postcode: str
    house_number: Union[int, str]
    suffix: str = ''


@dataclasses.dataclass
class LocationDescription:
    description: str


@dataclasses.dataclass
class Regions:
    regions: str


@dataclasses.dataclass
class SensorData:
    owner: PersonData
    reference: str
    type: str
    location: Union[LatLong, PostcodeHouseNumber, LocationDescription, Regions]
    datastream: str
    observation_goal: str
    themes: str
    contains_pi_data: Literal['Ja', 'Nee']
    legal_ground: str
    privacy_declaration: str
    active_until: Union[datetime.date, str]


IPROX_REGISTRATION_FIELDS = [
    'Verzonden',
    'Status',
    'Referentienummer',
    'Wilt u meer dan 5 sensoren melden?',
    'Vul uw e-mailadres in',
]

IPROX_PERSON_FIELDS = [
    'Naam organisatie/bedrijf',
    'Postcode',
    'Huisnummer',
    'Toevoeging',
    'Straatnaam',
    'Plaatsnaam',
    'E-mail',
    'Telefoon',
    'KVK-nummer',
    'Website',
    'Voornaam',
    'Tussenvoegsel',
    'Achternaam',
]

IPROX_SENSOR_FIELDS = [
    'Kies soort / type sensor',
    'Locatie sensor',
    'Hebt u een postcode en huisnummer?',
    'Postcode',
    'Huisnummer',
    'Toevoeging',
    'Omschrijving van de locatie van de sensor',
    'In welk gebied bevindt zich de mobiele sensor?',
    'Wat meet de sensor?',
    'Waarvoor meet u dat?',
    'Thema',
    'Worden er persoonsgegevens verwerkt?',
    'Wettelijke grondslag',
    'Privacyverklaring',
    'Tot wanneer is de sensor actief?',
    'Wilt u nog een sensor melden?',
]


ALL_IPROX_SENSOR_FIELDS = (IPROX_SENSOR_FIELDS * settings.IPROX_NUM_SENSORS)
IPROX_FIELDS = IPROX_REGISTRATION_FIELDS + IPROX_PERSON_FIELDS + ALL_IPROX_SENSOR_FIELDS


@dataclasses.dataclass
class Values:
    """
    Wraps a list of values from an excel file (either a row of columns, or
    column of rows) so that we can provide 'named access' to those values,
    e.g.

    >>> from collections import namedtuple
    >>> values = Values(['a', 'b', 'c'], [1, 2, 3])
    >>> values['a']
    1
    >>> values['d']
    Traceback (most recent call last):
      ...
    KeyError: 'd'

    It is possible to have duplicate keys, in which case slicing can be used
    to get the nth item (0 based) with a particular name, e.g.

    >>> values = Values(['a', 'a', 'a'], [10, 20, 30])
    >>> values['a', 2]
    30
    """
    fields: list
    values: list

    def __getitem__(self, field):
        """
        Get the item with the name field, if field is a tuple then the first
        item is the name of the field, the second item is the nth index to
        retrieve.
        """
        if isinstance(field, tuple):
            requested_field, nth = field
            matches = (i for i, field in enumerate(self.fields) if field == requested_field)
            matching_index = next(islice(matches, nth, nth + 1), None)
            if matching_index is not None:
                matching_value = self.values[matching_index]
                return matching_value.value if isinstance(matching_value, Cell) else matching_value
        else:
            # raise KeyError when field not present
            with contextlib.suppress(ValueError):
                matching_value = self.values[self.fields.index(field)]
                return matching_value.value if isinstance(matching_value, Cell) else matching_value

        # didn't return yet, then item could not be found
        raise KeyError(field)


@dataclasses.dataclass
class InvalidFields(ValueError):
    fields: list
    expected = NotImplemented

    def __str__(self):
        for actual_field, expected_field in zip_longest(self.fields, self.expected):
            if actual_field != expected_field:
                return f"Onverwachte veldnaam : {actual_field}, verwacht {expected_field}"


class InvalidIproxFields(InvalidFields):
    expected = IPROX_FIELDS


def parse_iprox_xlsx(workbook: Workbook) -> Generator[SensorData, None, None]:
    """
    Parse an iprox xlsx workbook, yielding all the sensor data that can be
    found in the file.
    """
    rows = workbook['Sensorregistratie'].rows
    fields = [cell.value for cell in next(rows, [])]
    if fields != IPROX_FIELDS:
        raise InvalidIproxFields(fields)

    for row in (Values(IPROX_FIELDS, row) for row in rows):

        owner = PersonData(
            organisation=row['Naam organisatie/bedrijf'],
            email=row['E-mail'],
            telephone=row['Telefoon'],
            website=row['Website'],
            first_name=row['Voornaam'],
            last_name_affix=row['Tussenvoegsel'],
            last_name=row['Achternaam'],
        )

        reference = row['Referentienummer']

        for sensor_number in range(settings.IPROX_NUM_SENSORS):

            if row['Locatie sensor'] == 'Vast':
                if row['Hebt u een postcode en huisnummer?'] == 'Ja':
                    # sensor_number + 1 since there is already a Postcode, Huisnummer and
                    # Toevoeging in the contact details :(
                    location = PostcodeHouseNumber(
                        row["Postcode", sensor_number + 1],
                        row["Huisnummer", sensor_number + 1],
                        row["Toevoeging", sensor_number + 1],
                    )
                else:
                    location = LocationDescription(
                        row['Omschrijving van de locatie van de sensor', sensor_number],
                    )
            else:
                location = Regions(
                    row['In welk gebied bevindt zich de mobiele sensor?', sensor_number]
                )

            yield SensorData(
                owner=owner,
                reference=f'{reference}.{sensor_number}',
                type=row["Kies soort / type sensor", sensor_number],
                location=location,
                datastream=row["Wat meet de sensor?", sensor_number],
                observation_goal=row["Waarvoor meet u dat?", sensor_number],
                themes=row["Thema", sensor_number],
                contains_pi_data=row["Worden er persoonsgegevens verwerkt?", sensor_number],
                legal_ground=row["Wettelijke grondslag", sensor_number],
                privacy_declaration=row["Privacyverklaring", sensor_number],
                active_until=row["Tot wanneer is de sensor actief?", sensor_number],
            )

            if row["Wilt u nog een sensor melden?", sensor_number] != 'Ja':
                break


BULK_PERSON_FIELDS = [
    'Naam organisatie/bedrijf',
    'Postcode',
    'Huisnummer',
    'Toevoeging (niet verplicht)',
    'Straatnaam',
    'Plaatsnaam',
    'E-mail',
    'Telefoon',
    'KVK-nummer (niet verplicht)',
    'Website (niet verplicht)',
    'Voornaam',
    'Tussenvoegsel (niet verplicht)',
    'Achternaam',
]

# Between iprox / bulk - we expect the same fields, they are just named
# differently
assert len(BULK_PERSON_FIELDS) == len(IPROX_PERSON_FIELDS)

BULK_SENSOR_FIELDS = [
    'Referentie',
    'Kies soort / type sensor',
    'Latitude',
    'Longitude',
    'Wat meet de sensor?',
    'Waarvoor meet u dat?',
    'Thema 1',
    'Thema 2 (niet verplicht)',
    'Thema 3 (niet verplicht)',
    'Thema 4 (niet verplicht)',
    'Thema 5 (niet verplicht)',
    'Thema 6 (niet verplicht)',
    'Thema 7 (niet verplicht)',
    'Thema 8 (niet verplicht)',
    'Worden er persoonsgegevens verwerkt?',
    'Wettelijke grondslag',
    'Privacyverklaring',
    'Tot wanneer is de sensor actief?',
    'Opmerking (niet verplicht)',
]


class InvalidPersonFields(InvalidFields):
    expected = BULK_PERSON_FIELDS


class InvalidSensorFields(InvalidFields):
    expected = BULK_SENSOR_FIELDS


def parse_bulk_xlsx(workbook: Workbook) -> Generator[SensorData, None, None]:
    """
    Parse a bulk excel, yielding all the sensors that are present in the file.
    """
    rows = list(workbook['Uw gegevens'].rows)
    fields = [row[0].value for row in rows]
    if fields != BULK_PERSON_FIELDS:
        raise InvalidPersonFields(fields)

    values = Values(BULK_PERSON_FIELDS, [row[1] for row in rows])
    owner = PersonData(
        organisation=values['Naam organisatie/bedrijf'],
        email=values['E-mail'],
        telephone=values['Telefoon'],
        website=values['Website (niet verplicht)'],
        first_name=values['Voornaam'],
        last_name_affix=values['Tussenvoegsel (niet verplicht)'],
        last_name=values['Achternaam'],
    )

    rows = workbook['Sensorregistratie'].rows
    fields = [cell.value for cell in next(rows, [])]
    if fields != BULK_SENSOR_FIELDS:
        raise InvalidSensorFields(fields)

    return (
        SensorData(
            owner=owner,
            reference=row["Referentie"],
            type=row["Kies soort / type sensor"],
            location=LatLong(
                row["Latitude"],
                row["Longitude"],
            ),
            datastream=row["Wat meet de sensor?"],
            observation_goal=row["Waarvoor meet u dat?"],
            themes=settings.IPROX_SEPARATOR.join(filter(None, [
                row["Thema 1"],
                row["Thema 2 (niet verplicht)"],
                row["Thema 3 (niet verplicht)"],
                row["Thema 4 (niet verplicht)"],
                row["Thema 5 (niet verplicht)"],
                row["Thema 6 (niet verplicht)"],
                row["Thema 7 (niet verplicht)"],
                row["Thema 8 (niet verplicht)"],
            ])),
            contains_pi_data=row["Worden er persoonsgegevens verwerkt?"],
            legal_ground=row["Wettelijke grondslag"],
            privacy_declaration=row["Privacyverklaring"],
            active_until=row["Tot wanneer is de sensor actief?"],
        )
        for row in (Values(BULK_SENSOR_FIELDS, row) for row in rows)
    )


def get_location(sensor_data: SensorData):
    """
    Get the specific django field and value which should be filled for the
    location data that was provided.
    """
    if isinstance(sensor_data.location, Regions):
        return {'regions': sensor_data.location.regions}
    elif isinstance(sensor_data.location, LatLong):
        return {'location': Point(*dataclasses.astuple(sensor_data.location))}
    elif isinstance(sensor_data.location, LocationDescription):
        return {'location_description': dataclasses.astuple(sensor_data.location)}
    elif isinstance(sensor_data.location, PostcodeHouseNumber):
        location = get_center_coordinates(
            sensor_data.location.postcode,
            sensor_data.location.house_number,
        )
        return {'location': location}
    else:
        raise TypeError(f'Onbekend locatie type {type(sensor_data.location)}')


@dataclasses.dataclass
class ValidationError(ValueError):
    sensor_data: SensorData
    source = NotImplemented
    target = NotImplemented

    def __str__(self):
        return f"Foutieve data voor sensor met referentie {self.sensor_data.reference} " \
               f" {self.source}={getattr(self.sensor_data, self.target)}"


class InvalidSensorType(ValidationError):
    source = 'Kies soort / type sensor'
    target = 'type'


class InvalidContainsPiData(ValidationError):
    source = 'Worden er persoonsgegevens verwerkt?'
    target = 'contains_pi_data'


class InvalidThemes(ValidationError):
    source = 'Thema'
    target = 'themes'


class InvalidLatitude(ValidationError):
    source = 'Latitude'
    target = 'latitude'


class InvalidLongitude(ValidationError):
    source = 'Longitude'
    target = 'longitude'


class InvalidLegalGround(ValidationError):
    source = 'Wettelijke grondslag'
    target = 'legal_ground'


class InvalidPostcode(ValidationError):
    source = 'Postcode'
    target = 'location'


class InvalidHouseNumber(ValidationError):
    source = 'Huisnummer'
    target = 'location'


class InvalidRegions(ValidationError):
    source = 'In welk gebied bevindt zich de mobiele sensor?'
    target = 'location'


class InvalidLocationDescription(ValidationError):
    source = 'Omschrijving van de locatie van de sensor'
    target = 'location'


class InvalidDate(ValidationError):
    source = 'Tot wanneer is de sensor actief?'
    target = 'active_until'


def validate_sensor(sensor_data: SensorData):
    """
    Ensure that the sensor data contains valid data, raises an exception when
    the data is invalid.
    """
    validate_type(sensor_data)
    validate_themes(sensor_data)
    validate_location(sensor_data)
    validate_contains_pi_data(sensor_data)
    validate_legal_ground(sensor_data)
    validate_active_until(sensor_data)


DATE_FORMAT = '%d-%m-%Y'


def validate_active_until(sensor_data):
    try:
        datetime.datetime.strptime(sensor_data.active_until, DATE_FORMAT)
    except Exception as e:
        raise InvalidDate(sensor_data) from e


def validate_legal_ground(sensor_data):
    if sensor_data.contains_pi_data == 'Ja':
        if sensor_data.legal_ground in (None, ''):
            raise InvalidLegalGround(sensor_data)


def validate_contains_pi_data(sensor_data):
    if sensor_data.contains_pi_data not in ("Ja", "Nee"):
        raise InvalidContainsPiData(sensor_data)


def validate_type(sensor_data):
    if sensor_data.type in ('', None):
        raise InvalidSensorType(sensor_data)


def validate_themes(sensor_data):
    themes = (sensor_data.themes or '').split(settings.IPROX_SEPARATOR)
    valid_themes = models.Theme.objects.filter(name__in=themes).count()
    if valid_themes != len(themes):
        raise InvalidThemes(sensor_data)


def validate_regions(sensor_data):
    if not sensor_data.location.regions:
        raise InvalidRegions(sensor_data)


def validate_location(sensor_data):
    if isinstance(sensor_data.location, Regions):
        validate_regions(sensor_data)
    elif isinstance(sensor_data.location, LatLong):
        validate_latitude_longitude(sensor_data)
    elif isinstance(sensor_data.location, PostcodeHouseNumber):
        validate_postcode_house_number(sensor_data)
    elif isinstance(sensor_data.location, LocationDescription):
        validate_location_description(sensor_data)


def validate_location_description(sensor_data):
    if not sensor_data.location.description:
        raise InvalidLocationDescription(sensor_data)


def validate_postcode_house_number(sensor_data):
    postcode_regex = r'\d\d\d\d ?[a-zA-Z][a-zA-Z]'
    if not sensor_data.location.postcode or \
            not re.match(postcode_regex, sensor_data.location.postcode):
        raise InvalidPostcode(sensor_data)


def validate_latitude_longitude(sensor_data):
    try:
        float(sensor_data.location.latitude)
    except Exception as e:
        raise InvalidLatitude(sensor_data) from e
    try:
        float(sensor_data.location.longitude)
    except Exception as e:
        raise InvalidLongitude(sensor_data) from e


def import_person(person_data: PersonData):
    """
    Import person data parsed from an iprox or bulk registration excel
    file.
    """
    names = [person_data.first_name]

    if person_data.last_name_affix:
        names.append(person_data.last_name_affix)

    names.append(person_data.last_name)

    owner, _ = models.Person2.objects.update_or_create(
        email=person_data.email, organisation=person_data.organisation,
        defaults={
            'name': ' '.join(names),
            'telephone': person_data.telephone,
            'website': person_data.website,
        }
    )

    return owner


def parse_date(value: Union[str, datetime.date, datetime.datetime]):
    """
    Parse a date value, it may be that the value came from loading an excel
    file in which case it will already be a date.
    """
    if isinstance(value, str):
        return datetime.datetime.strptime(value, DATE_FORMAT)
    elif isinstance(value, (datetime.date, datetime.datetime)):
        return value
    else:
        raise TypeError(f'Expected `str`, `date` or `datetime` instance got {type(value)}')


def import_sensor(sensor_data: SensorData, owner: models.Person2):
    """
    Import sensor data parsed from an iprox or bulk registration excel file.
    """
    defaults = {
        'type': models.Type2.objects.get_or_create(name=sensor_data.type)[0],
        'datastream': sensor_data.datastream,
        'observation_goal': sensor_data.observation_goal,
        'contains_pi_data': sensor_data.contains_pi_data == 'Ja',
        'active_until': parse_date(sensor_data.active_until),
        'owner': owner,
        'privacy_declaration': sensor_data.privacy_declaration,
    }

    location = get_location(sensor_data)
    if 'regions' not in location:
        defaults.update(location)

    if defaults['contains_pi_data']:
        defaults['legal_ground'] = models.LegalGround.objects.get_or_create(
            name=sensor_data.legal_ground
        )[0]

    # use the sensor_number to give each sensor a unique reference
    device, _ = models.Device2.objects.update_or_create(
        owner=owner,
        reference=sensor_data.reference,
        defaults=defaults,
    )

    if 'regions' in location:
        for region_name in location['regions'].split(settings.IPROX_SEPARATOR):
            region, _ = models.Region.objects.get_or_create(name=region_name)
            device.regions.add(region)

    for theme_name in sensor_data.themes.split(settings.IPROX_SEPARATOR):
        theme_id = models.id_from_name(models.Theme, theme_name)
        device.themes.add(theme_id)


def import_xlsx(workbook):
    """
    Load, parse and import person and sensor data from the given bulk or iprox
    excel file.

    :param workbook: openpyxl workbook containing excel data to import.

    :return: tuple containing lists of sensors : (errors, created, updated)
    """
    # For bulk registration the contact details are in a separate sheet
    parser = parse_bulk_xlsx if "Uw gegevens" in workbook else parse_iprox_xlsx
    sensors = list(parser(workbook))

    people = {
        person_data.email.lower(): import_person(person_data)
        for person_data in {s.owner.email.lower(): s.owner for s in sensors}.values()
    }

    created, updated, errors = [], [], []

    for sensor_data in sensors:
        try:
            validate_sensor(sensor_data)
            if import_sensor(sensor_data, people[sensor_data.owner.email.lower()]):
                created.append(sensor_data)
            else:
                updated.append(sensor_data)
        except Exception as e:
            errors.append(e)

    return errors, created, updated
