import contextlib
import dataclasses
import datetime
import re
from collections import Counter
from itertools import islice, zip_longest
from typing import Dict, Generator, List, Optional, Union

import requests
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.validators import URLValidator
from openpyxl import Workbook
from openpyxl.cell import Cell
from rest_framework import fields
from rest_framework.exceptions import ValidationError
from rest_framework.fields import EmailField
from rest_framework.serializers import Serializer
from typing_extensions import Literal

from iot import models


@dataclasses.dataclass
class PostcodeSearchException(ValueError):
    postcode: str
    house_number: int

    def __str__(self):
        return f"Ongeldige postcode ({self.postcode}) / huisnummer ({self.house_number})"


def normalize_postcode(postcode: str) -> str:
    return postcode.replace(' ', '').upper()


def get_postcode_url(postcode: str) -> str:
    normalized = normalize_postcode(postcode)
    return f'{settings.ATLAS_POSTCODE_SEARCH}/?q={normalized}'


def get_address_url(street: str, house_number: Union[int, str]) -> str:
    normalized = f'{street.lower()} {house_number}'
    return f'{settings.ATLAS_ADDRESS_SEARCH}/?q={normalized}'


def get_center_coordinates(postcode: str, house_number: Union[int, str]) -> Point:
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
        postcode_normalized = normalize_postcode(postcode)
        for result in data['results']:

            if 'centroid' not in result:
                raise PostcodeSearchException(postcode, house_number)

            if result.get('postcode') == postcode_normalized and \
                    str(result.get('huisnummer')) == str(house_number):
                centroid = result['centroid']
                return Point(centroid[0], centroid[1])

        # not found in this page, try next one
        url = data.get('_links')['next']['href']

    # If we got here it is because we didn't find a result with the correct
    # postcode and house number, so it seems this house number does not exist
    # for the given postcode.
    raise PostcodeSearchException(postcode, house_number)


class InvalidPersonDataError(ValidationError):
    def __str__(self):
        fields = self.args[0].detail.serializer.fields
        return "<br>".join(
            fields[field].source + ': ' + (','.join(str(e) for e in error_detail))
            for field, error_detail in self.args[0].args[0].items()
        )


class RequiredCharField(fields.CharField):
    def __init__(self, **kwargs):
        kwargs.setdefault('allow_blank', False)
        kwargs.setdefault('allow_null', False)
        super().__init__(**kwargs)


class OptionalCharField(fields.CharField):
    def __init__(self, **kwargs):
        kwargs.setdefault('allow_blank', True)
        kwargs.setdefault('allow_null', True)
        super().__init__(**kwargs)


class PersonDataSerializer(Serializer):
    organisation = OptionalCharField(max_length=255, source="Naam organisatie/bedrijf")
    email = EmailField(allow_blank=False, allow_null=False, source="E-mail")
    telephone = RequiredCharField(max_length=15, source="Telefoonnummer")
    website = fields.URLField(allow_blank=True, allow_null=True, source="Website")
    first_name = RequiredCharField(max_length=84, source="Voornaam")
    last_name_affix = OptionalCharField(max_length=84, source="Tussenvoegsel")
    last_name = RequiredCharField(max_length=84, source="Achternaam")


@dataclasses.dataclass
class PersonData:
    organisation: str
    email: str
    telephone: str
    website: str
    first_name: str
    last_name_affix: str
    last_name: str

    def validate(self):
        try:
            PersonDataSerializer(data=dataclasses.asdict(self)).is_valid(True)
        except ValidationError as e:
            raise InvalidPersonDataError(e) from e


@dataclasses.dataclass
class ObservationGoal:
    observation_goal: str
    privacy_declaration: str
    legal_ground: str


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
class Location:
    lat_long: Optional[LatLong]
    postcode_house_number: Optional[PostcodeHouseNumber]
    description: str
    regions: str


@dataclasses.dataclass
class SensorData:
    owner: PersonData
    reference: str
    type: str
    location: Location
    datastream: str
    observation_goals: List[ObservationGoal]
    themes: str
    contains_pi_data: Literal['Ja', 'Nee']
    active_until: Union[datetime.date, str]
    projects: List[str]
    row_number: Optional[int] = None


IPROX_REGISTRATION_FIELDS = [
    'Verzonden',
    'Status',
    'Referentienummer',
    'Wilt u meer dan 5 sensoren melden?',
    'Vul uw e-mailadres in',
]


IPROX_PERSON_FIELDS = [
    'Naam organisatie/bedrijf',
    'E-mail',
    'Postcode',
    'Huisnummer',
    'Toevoeging',
    'Straatnaam',
    'Plaatsnaam',
    'KVK-nummer',
    'Website',
    'Voornaam',
    'Tussenvoegsel',
    'Achternaam',
    'Telefoonnummer',
]

IPROX_SENSOR_FIELDS = [
    "Kies soort / type sensor",
    "Locatie sensor",
    "Hebt u een postcode en huisnummer?",
    "Postcode",
    "Huisnummer",
    "Toevoeging",
    "Omschrijving van de locatie van de sensor",
    "In welk gebied bevindt zich de mobiele sensor?",
    "Wat meet de sensor?",
    "Waarvoor meet u dat?",
    "Kies een of meerdere thema's",
    "Worden er persoonsgegevens verwerkt?",
    "Privacyverklaring",
    "Wettelijke grondslag",
    "Wanneer wordt de sensor verwijderd?",
    "Wilt u nog een sensor melden?",
]


ALL_IPROX_SENSOR_FIELDS = (IPROX_SENSOR_FIELDS * settings.IPROX_NUM_SENSORS)
# Last sensor does not have "Wilt u nog een sensor melden?"
ALL_IPROX_SENSOR_FIELDS.pop()
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

    def get(self, field, default=None):
        try:
            return self[field]
        except KeyError:
            return default

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
                val = matching_value.value if isinstance(matching_value, Cell) else matching_value
                return val.strip() if isinstance(val, str) else val
        else:
            # raise KeyError when field not present
            with contextlib.suppress(ValueError):
                matching_value = self.values[self.fields.index(field)]
                val = matching_value.value if isinstance(matching_value, Cell) else matching_value
                return val.strip() if isinstance(val, str) else val

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
        return "Onverwachte velden"


class InvalidIproxFields(InvalidFields):
    expected = IPROX_FIELDS


def parse_iprox_xlsx(workbook: Workbook) -> Generator[SensorData, None, None]:
    """
    Parse an iprox xlsx workbook, yielding all the sensor data that can be
    found in the file.
    """
    rows = workbook['Sensorregistratie'].rows
    fields = [
        cell.value
        for i, cell in enumerate(next(rows, []))
        if i < len(IPROX_FIELDS)  # ignore columns after expected data
    ]
    if fields != IPROX_FIELDS:
        raise InvalidIproxFields(fields)

    for row_number, row in enumerate(Values(IPROX_FIELDS, row) for row in rows):

        # Don't process an empty row in the excel file
        referentienummer = row.get('Referentienummer') or ''
        if not referentienummer.strip():
            continue

        owner = PersonData(
            organisation=row['Naam organisatie/bedrijf'],
            email=row['E-mail'],
            telephone=row['Telefoonnummer'],
            website=row['Website'],
            first_name=row['Voornaam'],
            last_name_affix=row['Tussenvoegsel'],
            last_name=row['Achternaam'],
        )

        reference = row['Referentienummer']

        for sensor_index in range(settings.IPROX_NUM_SENSORS):

            location_postcode = None

            if row['Locatie sensor'] == 'Vast':
                if row['Hebt u een postcode en huisnummer?'] == 'Ja':
                    # sensor_index + 1 since there is already a Postcode, Huisnummer and
                    # Toevoeging in the contact details :(
                    location_postcode = PostcodeHouseNumber(
                        row["Postcode", sensor_index + 1],
                        row["Huisnummer", sensor_index + 1],
                        row["Toevoeging", sensor_index + 1],
                    )

            location_description = row.get(
                'Omschrijving van de locatie van de sensor', sensor_index
            ) or ''

            regions = row.get('In welk gebied bevindt zich de mobiele sensor?', sensor_index) or ''

            location = Location(
                postcode_house_number=location_postcode,
                description=location_description,
                regions=regions,
                lat_long=None
            )

            yield SensorData(
                owner=owner,
                reference=f'{reference}.{sensor_index}',
                type=row["Kies soort / type sensor", sensor_index],
                location=location,
                datastream=row["Wat meet de sensor?", sensor_index],
                observation_goals=[ObservationGoal(
                    observation_goal=row["Waarvoor meet u dat?", sensor_index],
                    privacy_declaration=row["Privacyverklaring", sensor_index],
                    legal_ground=row["Wettelijke grondslag", sensor_index]
                )],
                themes=row["Kies een of meerdere thema's", sensor_index],
                contains_pi_data=row["Worden er persoonsgegevens verwerkt?", sensor_index],
                active_until=row["Wanneer wordt de sensor verwijderd?", sensor_index],
                projects=[''],  # not required for the iprox
                row_number=row_number + 1,
            )

            if row.get(("Wilt u nog een sensor melden?", sensor_index), 'Nee') != 'Ja':
                break


BULK_PERSON_FIELDS = [
    'Naam organisatie/bedrijf',
    'Postcode',
    'Huisnummer',
    'Toevoeging (niet verplicht)',
    'Straatnaam',
    'Plaatsnaam',
    'E-mail',
    'Telefoonnummer',
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
    'In welk gebied bevindt zich de mobiele sensor?',
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
    'Wanneer wordt de sensor verwijderd?',
    'Opmerking (niet verplicht)',
    'Project',
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
    fields = [
        row[0].value
        for i, row in enumerate(rows)
        if i < len(BULK_PERSON_FIELDS)  # ignore any rows after the expected data
    ]
    if fields != BULK_PERSON_FIELDS:
        raise InvalidPersonFields(fields)

    values = Values(BULK_PERSON_FIELDS, [row[1] for row in rows])
    owner = PersonData(
        organisation=values['Naam organisatie/bedrijf'],
        email=values['E-mail'],
        telephone=values['Telefoonnummer'],
        website=values['Website (niet verplicht)'],
        first_name=values['Voornaam'],
        last_name_affix=values['Tussenvoegsel (niet verplicht)'],
        last_name=values['Achternaam'],
    )

    rows = workbook['Sensorregistratie'].rows
    fields = [
        cell.value
        for i, cell in enumerate(next(rows, []))
        if i < len(BULK_SENSOR_FIELDS)  # ignore all columns after the expected data
    ]
    if fields != BULK_SENSOR_FIELDS:
        raise InvalidSensorFields(fields)

    return (
        SensorData(
            owner=owner,
            reference=row["Referentie"],
            type=row["Kies soort / type sensor"],
            location=Location(
                lat_long=LatLong(
                    row["Latitude"],
                    row["Longitude"]
                ),
                postcode_house_number=None,
                description='',
                regions=row.get('In welk gebied bevindt zich de mobiele sensor?') or ''
            ),
            datastream=row["Wat meet de sensor?"],
            observation_goals=[ObservationGoal(
                observation_goal=row["Waarvoor meet u dat?"],
                privacy_declaration=row["Privacyverklaring"],
                legal_ground=row["Wettelijke grondslag"]
            )],
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
            active_until=row["Wanneer wordt de sensor verwijderd?"],
            projects=[row.get('Project') or ''],
            row_number=row_number + 1,
        )
        for row_number, row in enumerate(Values(BULK_SENSOR_FIELDS, row) for row in rows)
        if (row['Referentie'] or '').strip()  # Ignore any rows with an empty reference
    )


def get_location(sensor_data: SensorData) -> Dict:
    """
    Get the specific django field and value which should be filled for the
    location data that was provided. It will return a dict of one or multiple locations.
    """
    locations = {}  # empty dict to hold the locations.
    if sensor_data.location.regions:
        locations['regions'] = sensor_data.location.regions
    if isinstance(sensor_data.location.lat_long, LatLong):
        locations['location'] = Point(
            sensor_data.location.lat_long.longitude,
            sensor_data.location.lat_long.latitude
        )
    if sensor_data.location.description:
        locations['location_description'] = sensor_data.location.description
    if isinstance(sensor_data.location.postcode_house_number, PostcodeHouseNumber):
        location = get_center_coordinates(
            sensor_data.location.postcode_house_number.postcode,
            sensor_data.location.postcode_house_number.house_number,
        )
        locations['location'] = location
    # if the locations dict is empty, raise an exception otherwise return it.
    if locations:
        return locations
    else:
        raise TypeError(f'Onbekend locatie type {type(sensor_data.location)}')


@dataclasses.dataclass
class SensorValidationError(ValueError):
    sensor_data: SensorData
    source = NotImplemented
    target = NotImplemented

    def __str__(self):
        return f"Foutieve data voor sensor met referentie {self.sensor_data.reference} " \
               f" (rij {self.sensor_data.row_number}) {self.source}=" \
               f"{getattr(self.sensor_data, self.target)}"


class InvalidSensorType(SensorValidationError):
    source = 'Kies soort / type sensor'
    target = 'type'


class InvalidContainsPiData(SensorValidationError):
    source = 'Worden er persoonsgegevens verwerkt?'
    target = 'contains_pi_data'


class InvalidThemes(SensorValidationError):
    source = 'Thema'
    target = 'themes'


class InvalidLatitude(SensorValidationError):
    source = 'Latitude'
    target = 'location'


class InvalidLongitude(SensorValidationError):
    source = 'Longitude'
    target = 'location'


class InvalidLegalGround(SensorValidationError):
    source = 'Wettelijke grondslag'
    target = 'legal_ground'


class InvalidPostcode(SensorValidationError):
    source = 'Postcode'
    target = 'location'


class InvalidHouseNumber(SensorValidationError):
    source = 'Huisnummer'
    target = 'location'


class InvalidRegions(SensorValidationError):
    source = 'In welk gebied bevindt zich de mobiele sensor?'
    target = 'location'


class InvalidLocationDescription(SensorValidationError):
    source = 'Omschrijving van de locatie van de sensor'
    target = 'location'


class InvalidDate(SensorValidationError):
    source = 'Wanneer wordt de sensor verwijderd?'
    target = 'active_until'


class InvalidPrivacyDeclaration(SensorValidationError):
    source = 'Privacyverklaring'
    target = 'privacy_declaration'


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
    validate_privacy_declaration(sensor_data)
    validate_active_until(sensor_data)


DATE_FORMAT = '%d-%m-%Y'


def validate_active_until(sensor_data):
    try:
        datetime.datetime.strptime(sensor_data.active_until, DATE_FORMAT)
    except Exception as e:
        raise InvalidDate(sensor_data) from e


def validate_privacy_declaration(sensor_data):
    # store the valid privacy_declarations
    privacy_declarations_list = []
    for observation_goal in sensor_data.observation_goals:
        privacy_declaration = (observation_goal.privacy_declaration or '').strip()
        if privacy_declaration:
            try:
                URLValidator()(privacy_declaration)
            except Exception as e:
                raise InvalidPrivacyDeclaration(sensor_data) from e
        # append the privacy_declarations into the list
        privacy_declarations_list.append(privacy_declaration)

    # if the contains_pi_data is True and none of the privacy_delcarations is valid,
    # raise the InvalidPrivacyDeclaration exception.
    # This could move to be a seperate validator function also.
    if sensor_data.contains_pi_data == 'Ja' and not any(privacy_declarations_list):
        raise InvalidPrivacyDeclaration(sensor_data)


def validate_legal_ground(sensor_data):
    if sensor_data.contains_pi_data == 'Ja':
        for observation_goal in sensor_data.observation_goals:
            if observation_goal.legal_ground in (None, ''):
                raise InvalidLegalGround(sensor_data)


def validate_contains_pi_data(sensor_data):
    if sensor_data.contains_pi_data not in ("Ja", "Nee"):
        raise InvalidContainsPiData(sensor_data)


def validate_type(sensor_data):
    type = (sensor_data.type or '').strip()
    if not type:
        raise InvalidSensorType(sensor_data)


def validate_themes(sensor_data):
    themes = (sensor_data.themes or '').strip()
    if not themes:
        raise InvalidThemes(sensor_data)


def validate_location(sensor_data):
    if isinstance(sensor_data.location.lat_long, LatLong):
        validate_latitude_longitude(sensor_data)
    elif isinstance(sensor_data.location.postcode_house_number, PostcodeHouseNumber):
        validate_postcode_house_number(sensor_data)


def validate_postcode_house_number(sensor_data):
    postcode_regex = r'\d\d\d\d ?[a-zA-Z][a-zA-Z]'
    if not sensor_data.location.postcode_house_number.postcode or \
            not re.match(postcode_regex, sensor_data.location.postcode_house_number.postcode):
        raise InvalidPostcode(sensor_data)


def validate_latitude_longitude(sensor_data):
    try:
        float(sensor_data.location.lat_long.latitude)
    except Exception as e:
        raise InvalidLatitude(sensor_data) from e
    try:
        float(sensor_data.location.lat_long.longitude)
    except Exception as e:
        raise InvalidLongitude(sensor_data) from e


def import_person(person_data: PersonData, action_logger=lambda x: x):
    """
    Import person data parsed from an iprox or bulk registration excel
    file.
    """
    names = [person_data.first_name]

    if person_data.last_name_affix:
        names.append(person_data.last_name_affix)

    names.append(person_data.last_name)

    owner, _ = action_logger(models.Person2.objects.update_or_create(
        email=person_data.email, organisation=person_data.organisation,
        defaults={
            'name': ' '.join(names),
            'telephone': person_data.telephone,
            'website': person_data.website,
        },
    ))

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


def import_sensor(sensor_data: SensorData, owner: models.Person2, action_logger=lambda x: x):
    """
    Import sensor data parsed from an iprox or bulk registration excel file.
    """

    defaults = {
        'type': action_logger(models.Type2.objects.get_or_create(name=sensor_data.type))[0],
        'datastream': sensor_data.datastream,
        'contains_pi_data': sensor_data.contains_pi_data == 'Ja',
        'active_until': parse_date(sensor_data.active_until),
        'owner': owner,
    }
    location = get_location(sensor_data)
    # update the defaults with only the location and location_description. This will
    # allow the locations + regions if set to be added to the device.
    defaults.update(
        {k: v for k, v in location.items() if k in ['location', 'location_description']}
    )

    # use the sensor_index to give each sensor a unique reference
    device, created = action_logger(models.Device2.objects.update_or_create(
        owner=owner,
        reference=sensor_data.reference,
        defaults=defaults,
    ))

    if 'regions' in location:
        for region_name in location['regions'].split(settings.IPROX_SEPARATOR):
            region = action_logger(models.Region.objects.get_or_create(name=region_name))[0]
            device.regions.add(region)

    for theme_name in sensor_data.themes.split(settings.IPROX_SEPARATOR):
        theme = models.Theme.objects.get_or_create(name=theme_name)[0]
        device.themes.add(theme)

    for observation_goal in sensor_data.observation_goals:

        # only create a legal_ground if it's not empty string and valid, otherwise make it None.
        legal_ground = None if not observation_goal.legal_ground else \
            action_logger(models.LegalGround.objects.get_or_create(
                name=observation_goal.legal_ground))[0]

        import_result = action_logger(models.ObservationGoal.objects.get_or_create(
            observation_goal=observation_goal.observation_goal,
            privacy_declaration=observation_goal.privacy_declaration,
            legal_ground=legal_ground))[0]
        device.observation_goals.add(import_result)

    for project in sensor_data.projects:
        # only import the projects if the list is not empty
        if project:
            path = project.split(settings.IPROX_SEPARATOR)
            # because it's a list of string, convert every string to a list because it's an
            # arrayfield that will take a list of string for each path.
            project_paths = action_logger(models.Project.objects.get_or_create(
                path=path))[0]
            device.projects.add(project_paths)

    return device, created


@dataclasses.dataclass
class DuplicateReferenceError(Exception):
    reference: str
    count: int

    def __str__(self):
        return f"Referenties moeten uniek zijn: {self.reference} komt {self.count} keer voor"


def import_xlsx(workbook, action_logger=lambda x: x):
    """
    Load, parse and import person and sensor data from the given bulk or iprox
    excel file.

    :param workbook: openpyxl workbook containing excel data to import.

    :return: tuple containing lists of sensors : (errors, created, updated)
    """
    # For bulk registration the contact details are in a separate sheet
    parser = parse_bulk_xlsx if "Uw gegevens" in workbook else parse_iprox_xlsx
    sensors = list(parser(workbook))

    sensor_counter = Counter(sensor.reference for sensor in sensors)
    errors: List[Exception] = [
        DuplicateReferenceError(reference, count)
        for reference, count in sensor_counter.most_common()
        if count > 1
    ]
    if errors:
        return errors, 0, 0

    for sensor in sensors:
        try:
            sensor.owner.validate()
        except Exception as e:
            raise Exception(f"Foutieve persoon data voor {sensor.reference}"
                            f" (rij {sensor.row_number}): {e}") from e

    imported_owners = {
        person_data.email.lower(): import_person(person_data, action_logger)
        for person_data in [s.owner for s in sensors]
    }

    counter = Counter()

    imported_sensors = []
    for sensor_data in sensors:
        try:
            validate_sensor(sensor_data)
            owner = imported_owners[sensor_data.owner.email.lower()]
            sensor, created = import_sensor(sensor_data, owner, action_logger)
            imported_sensors.append(sensor)
            counter.update([created])
        except Exception as e:
            errors.append(e)

    return errors, imported_sensors, counter[True], counter[False]
