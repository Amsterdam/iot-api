from collections import Counter
from typing import Generator, List

from django.conf import settings
from openpyxl import Workbook
from rest_framework.exceptions import ValidationError

from iot.constants.sensor_fields import (
    BULK_PERSON_FIELDS,
    BULK_SENSOR_FIELDS,
    IPROX_FIELDS,
)
from iot.dateclasses import (
    LatLong,
    Location,
    ObservationGoal,
    PersonData,
    PostcodeHouseNumber,
    SensorData,
)
from iot.importers.import_person import import_person
from iot.importers.import_sensor import import_sensor
from iot.utils import Values
from iot.validators import validate_person_data, validate_sensor


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
        ValidationError(reference, count)
        for reference, count in sensor_counter.most_common()
        if count > 1
    ]
    if errors:
        return errors, 0, 0

    for sensor in sensors:
        try:
            validate_person_data(sensor.owner)
        except Exception as e:
            raise Exception(
                f"Foutieve persoon data voor {sensor.reference}"
                f" (rij {sensor.row_number}): {e}"
            ) from e

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
        raise ValidationError(fields)

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
        raise ValidationError(fields)

    return (
        SensorData(
            owner=owner,
            reference=row["Referentie"],
            type=row["Kies soort / type sensor"],
            location=Location(
                lat_long=LatLong(row["Latitude"], row["Longitude"]),
                postcode_house_number=None,
                description='',
                regions=row.get('In welk gebied bevindt zich de mobiele sensor?') or '',
            ),
            datastream=row["Wat meet de sensor?"],
            observation_goals=[
                ObservationGoal(
                    observation_goal=row["Waarvoor meet u dat?"],
                    privacy_declaration=row["Privacyverklaring"],
                    legal_ground=row["Wettelijke grondslag"],
                )
            ],
            themes=settings.IPROX_SEPARATOR.join(
                filter(
                    None,
                    [
                        row["Thema 1"],
                        row["Thema 2 (niet verplicht)"],
                        row["Thema 3 (niet verplicht)"],
                        row["Thema 4 (niet verplicht)"],
                        row["Thema 5 (niet verplicht)"],
                        row["Thema 6 (niet verplicht)"],
                        row["Thema 7 (niet verplicht)"],
                        row["Thema 8 (niet verplicht)"],
                    ],
                )
            ),
            contains_pi_data=row["Worden er persoonsgegevens verwerkt?"],
            active_until=row["Wanneer wordt de sensor verwijderd?"],
            projects=[row.get('Project') or ''],
            row_number=row_number + 1,
        )
        for row_number, row in enumerate(
            Values(BULK_SENSOR_FIELDS, row) for row in rows
        )
        if (row['Referentie'] or '').strip()  # Ignore any rows with an empty reference
    )


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
        raise ValidationError(fields)

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

            location_description = (
                row.get('Omschrijving van de locatie van de sensor', sensor_index) or ''
            )

            regions = (
                row.get('In welk gebied bevindt zich de mobiele sensor?', sensor_index)
                or ''
            )

            location = Location(
                postcode_house_number=location_postcode,
                description=location_description,
                regions=regions,
                lat_long=None,
            )

            yield SensorData(
                owner=owner,
                reference=f'{reference}.{sensor_index}',
                type=row["Kies soort / type sensor", sensor_index],
                location=location,
                datastream=row["Wat meet de sensor?", sensor_index],
                observation_goals=[
                    ObservationGoal(
                        observation_goal=row["Waarvoor meet u dat?", sensor_index],
                        privacy_declaration=row["Privacyverklaring", sensor_index],
                        legal_ground=row["Wettelijke grondslag", sensor_index],
                    )
                ],
                themes=row["Kies een of meerdere thema's", sensor_index],
                contains_pi_data=row[
                    "Worden er persoonsgegevens verwerkt?", sensor_index
                ],
                active_until=row["Wanneer wordt de sensor verwijderd?", sensor_index],
                projects=[''],  # not required for the iprox
                row_number=row_number + 1,
            )

            if row.get(("Wilt u nog een sensor melden?", sensor_index), 'Nee') != 'Ja':
                break
