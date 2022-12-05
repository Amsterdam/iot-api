from typing import Dict, Union

import requests
from django.conf import settings
from django.contrib.gis.geos import Point
from rest_framework.exceptions import ValidationError

from iot import models
from iot.dateclasses import LatLong, PostcodeHouseNumber, SensorData
from iot.utils import parse_date, remove_all

STADSDEEL_TO_STADSDEEL_CODE_MAPPING = {
    "Stadsdeel Centrum": "A",
    "Stadsdeel Oost": "M",
    "Stadsdeel Westpoort": "B",
    "Stadsdeel Nieuw-West": "F",
    "Stadsdeel Zuidoost": "T",
    "Stadsdeel Noord": "N",
    "Stadsdeel West": "E",
    "Stadsdeel Weesp": "S",
    "Stadsdeel Zuid": "K",
}


def import_sensor(
    sensor_data: SensorData, owner: models.Person, action_logger=lambda x: x
):
    """
    Import sensor data parsed from an iprox or bulk registration excel file.
    """

    defaults = {
        'type': action_logger(models.Type.objects.get_or_create(name=sensor_data.type))[
            0
        ],
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
    device, created = action_logger(
        models.Device.objects.update_or_create(
            owner=owner,
            reference=sensor_data.reference,
            defaults=defaults,
        )
    )

    # many2many relations
    remove_all(device.regions)
    if 'regions' in location:
        for region_name in location['regions'].split(settings.IPROX_SEPARATOR):
            region = action_logger(
                models.Region.objects.get_or_create(
                    name=STADSDEEL_TO_STADSDEEL_CODE_MAPPING.get(
                        region_name, region_name
                    )
                )
            )[0]
            device.regions.add(region)

    remove_all(device.themes)
    for theme_name in sensor_data.themes.split(settings.IPROX_SEPARATOR):
        theme = models.Theme.objects.get_or_create(name=theme_name)[0]
        device.themes.add(theme)

    remove_all(device.observation_goals)
    for observation_goal in sensor_data.observation_goals:

        # only create a legal_ground if it's not empty string and valid, otherwise make it None.
        legal_ground = (
            None
            if not observation_goal.legal_ground
            else action_logger(
                models.LegalGround.objects.get_or_create(
                    name=observation_goal.legal_ground
                )
            )[0]
        )

        import_result = action_logger(
            models.ObservationGoal.objects.get_or_create(
                observation_goal=observation_goal.observation_goal,
                privacy_declaration=observation_goal.privacy_declaration,
                legal_ground=legal_ground,
            )
        )[0]
        device.observation_goals.add(import_result)

    remove_all(device.projects)
    for project in sensor_data.projects:
        # only import the projects if the list is not empty
        if project:
            path = project.split(settings.IPROX_SEPARATOR)
            # because it's a list of string, convert every string to a list because it's an
            # arrayfield that will take a list of string for each path.
            project_paths = action_logger(
                models.Project.objects.get_or_create(path=path)
            )[0]
            device.projects.add(project_paths)

    return device, created


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
            sensor_data.location.lat_long.latitude,
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


def get_center_coordinates(postcode: str, house_number: Union[int, str]) -> Point:
    """
    :return: The centroid longitude and latitude coordinates for a postcode and
             the house number on that street.
    """
    url = get_postcode_url(postcode)
    data = requests.get(url).json()

    if not data or not data.get('results') or 'naam' not in data['results'][0]:
        raise ValidationError(postcode, house_number)

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
                raise ValidationError(postcode, house_number)

            if result.get('postcode') == postcode_normalized and str(
                result.get('huisnummer')
            ) == str(house_number):
                centroid = result['centroid']
                return Point(centroid[0], centroid[1])

        # not found in this page, try next one
        url = data.get('_links')['next']['href']

    # If we got here it is because we didn't find a result with the correct
    # postcode and house number, so it seems this house number does not exist
    # for the given postcode.
    raise ValidationError(postcode, house_number)


def normalize_postcode(postcode: str) -> str:
    return postcode.replace(' ', '').upper()


def get_postcode_url(postcode: str) -> str:
    normalized = normalize_postcode(postcode)
    return f'{settings.ATLAS_POSTCODE_SEARCH}/?q={normalized}'


def get_address_url(street: str, house_number: Union[int, str]) -> str:
    normalized = f'{street.lower()} {house_number}'
    return f'{settings.ATLAS_ADDRESS_SEARCH}/?q={normalized}'
