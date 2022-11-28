import dataclasses
import datetime
import re

from django.core.validators import URLValidator
from rest_framework.exceptions import ValidationError

from iot.dateclasses import SensorData, LatLong, PostcodeHouseNumber
from iot.exceptions import InvalidDate, InvalidPersonDataError, InvalidSensorType, InvalidThemes, InvalidLatitude, \
    InvalidLongitude, InvalidPostcode, InvalidContainsPiData, InvalidLegalGround, InvalidPrivacyDeclaration
from iot.serializers import PersonDataSerializer
from iot.utils import DATE_FORMAT


def validate_active_until(sensor_data):
    try:
        datetime.datetime.strptime(sensor_data.active_until, DATE_FORMAT)
    except Exception as e:
        raise InvalidDate(sensor_data) from e


def validate_person_data(self):
    try:
        PersonDataSerializer(data=dataclasses.asdict(self)).is_valid(
            raise_exception=True
        )
    except ValidationError as e:
        raise InvalidPersonDataError(e) from e


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


def validate_type(sensor_data):
    type = (sensor_data.type or '').strip()
    if not type:
        raise InvalidSensorType(sensor_data)


def validate_themes(sensor_data):
    themes = (sensor_data.themes or '').strip()
    if not themes:
        raise InvalidThemes(sensor_data)


def validate_location(sensor_data):
    def validate_latitude_longitude(sensor_data):
        try:
            float(sensor_data.location.lat_long.latitude)
        except Exception as e:
            raise InvalidLatitude(sensor_data) from e
        try:
            float(sensor_data.location.lat_long.longitude)
        except Exception as e:
            raise InvalidLongitude(sensor_data) from e

    def validate_postcode_house_number(sensor_data):
        postcode_regex = r'\d\d\d\d ?[a-zA-Z][a-zA-Z]'
        if not sensor_data.location.postcode_house_number.postcode or not re.match(
            postcode_regex, sensor_data.location.postcode_house_number.postcode
        ):
            raise InvalidPostcode(sensor_data)

    if isinstance(sensor_data.location.lat_long, LatLong):
        validate_latitude_longitude(sensor_data)
    elif isinstance(sensor_data.location.postcode_house_number, PostcodeHouseNumber):
        validate_postcode_house_number(sensor_data)


def validate_contains_pi_data(sensor_data):
    if sensor_data.contains_pi_data not in ("Ja", "Nee"):
        raise InvalidContainsPiData(sensor_data)


def validate_legal_ground(sensor_data):
    if sensor_data.contains_pi_data == 'Ja':
        for observation_goal in sensor_data.observation_goals:
            if observation_goal.legal_ground in (None, ''):
                raise InvalidLegalGround(sensor_data)


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