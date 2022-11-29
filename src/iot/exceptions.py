import dataclasses
from itertools import zip_longest

from rest_framework.exceptions import ValidationError

from iot.constants.sensor_fields import (
    BULK_PERSON_FIELDS,
    BULK_SENSOR_FIELDS,
    IPROX_FIELDS,
)
from iot.dateclasses import SensorData


class InvalidPersonDataError(ValidationError):
    def __str__(self):
        fields = self.args[0].detail.serializer.fields
        return "<br>".join(
            fields[field].source + ': ' + (','.join(str(e) for e in error_detail))
            for field, error_detail in self.args[0].args[0].items()
        )


@dataclasses.dataclass
class InvalidFields(ValueError):
    fields: list
    expected = NotImplemented

    def __str__(self):
        for actual_field, expected_field in zip_longest(self.fields, self.expected):
            if actual_field != expected_field:
                return (
                    f"Onverwachte veldnaam : {actual_field}, verwacht {expected_field}"
                )
        return "Onverwachte velden"


class InvalidIproxFields(InvalidFields):
    expected = IPROX_FIELDS


class InvalidPersonFields(InvalidFields):
    expected = BULK_PERSON_FIELDS


class InvalidSensorFields(InvalidFields):
    expected = BULK_SENSOR_FIELDS


@dataclasses.dataclass
class SensorValidationError(ValueError):
    sensor_data: SensorData
    source = NotImplemented
    target = NotImplemented

    def __str__(self):
        return (
            f"Foutieve data voor sensor met referentie {self.sensor_data.reference} "
            f" (rij {self.sensor_data.row_number}) {self.source}="
            f"{getattr(self.sensor_data, self.target)}"
        )


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


@dataclasses.dataclass
class DuplicateReferenceError(Exception):
    reference: str
    count: int

    def __str__(self):
        return f"Referenties moeten uniek zijn: {self.reference} komt {self.count} keer voor"


@dataclasses.dataclass
class PostcodeSearchException(ValueError):
    postcode: str
    house_number: int

    def __str__(self):
        return (
            f"Ongeldige postcode ({self.postcode}) / huisnummer ({self.house_number})"
        )
