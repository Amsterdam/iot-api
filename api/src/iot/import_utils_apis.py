from collections import Counter
from typing import Generator, List

import requests
from django.conf import settings

from iot import import_utils, models
from iot.import_utils import LatLong, PersonData, SensorData

PARSERS_MAPPER = {
    'wifi_sensor_crowd_management': 'parse_wifi_sensor_crowd_management',
    'camera_brug_en_sluisbediening': 'parse_camera_brug_en_sluisbediening',
    'cctv_camera_verkeersmanagement': 'parse_cctv_camera_verkeersmanagement',
    'kentekencamera_reistijd': 'parse_kentekencamera_reistijd',
    'kentekencamera_milieuzone': 'parse_kkentekencamera_milieuzone',
    'ais_masten': 'parse_ais_masten',
    'verkeersonderzoek_met_cameras': 'parse_verkeersonderzoek_met_cameras',
    'beweegbare_fysieke_afsluiting': 'parse_beweegbare_fysieke_afsluiting',
}


def import_api_data(api_name: str, api_url: str) -> str:
    """
    takes the name of the api as a param, execute the parser that belongs
    to the function. The parser will return a generator of SensorData.
    from the generator, use the import_person_data and import_senso_data.
    """
    # make a request and get the json data. covert it to a dict
    # return f'ERROR importing data from api {api_name}: {globals()}'
    try:
        response = requests.get(url=api_url)
        # check if response is 200 and content type is json, if not, return
        if response.status_code != 200 or \
                'application/json' not in response.headers["Content-Type"]:
            return f'ERROR importing api {api_name}: {response.status_code} - {response.content}'

        data = response.json()
        parser = globals().get(PARSERS_MAPPER[api_name])

        sensors = list(parser(data))
        owners_list = [sensor.owner for sensor in sensors]
        # return f'ERROR importing data from api {api_name}: {sensors}'

        for owner in owners_list:
            owner.validate()

        imported_owners = {
            person_data.email.lower(): import_utils.import_person(person_data)
            for person_data in owners_list
        }

        counter = Counter()

        errors: List[Exception] = []  # empty list to holding exceptions
        for sensor_data in sensors:
            try:
                import_utils.validate_sensor(sensor_data)
                owner = imported_owners[sensor_data.owner.email.lower()]
                _, created = import_utils.import_sensor(sensor_data, owner)
                counter.update([created])
            except Exception as e:
                errors.append(e)

        # delete sensors from the same owner that are not in the api
        delete_not_found_sendors(sensors=sensors, person=owners_list[0])

        return f'OK: {api_name} err: {errors}, succ: {counter[True]}'
        # return f'sensor: {len(sensors)} - owners: {len(owners_list)} - {imported_owners}'
    except Exception as e:
        return f'ERROR importing data from api {api_name}: {e}'


def parse_wifi_sensor_crowd_management(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the crowd management data list of dictionaries into SensorData objects and
    yield it. Yield only the sensors with Soort == WiFi sensor.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    personData = PersonData(
        organisation='Gemeente Amsterdam',
        email='LVMA@amsterdam.nl',
        telephone='06123456',
        website='https://acc.sensorenregister.amsterdam.nl',
        first_name='verkeers',
        last_name_affix='v',
        last_name='onderzoek'
    )

    # sensors_list = []
    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            properties = feature['properties']  # properties dict

            # filter only the sonsor with the WiFi sensor soort.
            if properties['Soort'] != 'WiFi sensor':
                continue
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][0]
            longitude = geometry['coordinates'][1]

            # sensors_list.append(
            yield SensorData(
                owner=personData,
                reference=feature['id'],
                type='Feature',
                location=LatLong(latitude=latitude, longitude=longitude),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagment in de rol van wegbeheerder.',
                privacy_declaration=properties['Privacyverklaring'],
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goal='Tellen van mensen.',
                active_until='01-01-2050'
            )


def parse_camera_brug_en_sluisbediening(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the camera brug en sluisbediening data list of dictionaries into SensorData objects and
    yield it.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    personData = PersonData(
        organisation='Gemeente Amsterdam',
        email='stedelijkbeheer@amsterdam.nl',
        telephone='06123456',
        website='https://acc.sensorenregister.amsterdam.nl',
        first_name='stedelijk',
        last_name_affix='v',
        last_name='beheer'
    )

    # sensors_list = []
    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][0]
            longitude = geometry['coordinates'][1]
            properties = feature['properties']  # properties dict

            yield SensorData(
                owner=personData,
                reference=feature['id'],
                type='Feature',
                location=LatLong(latitude=latitude, longitude=longitude),
                contains_pi_data='Ja',
                legal_ground='Sluisbeheerder in het kader van de woningwet 1991',
                privacy_declaration=properties['Privacyverklaring'],
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goal='Het bedienen van sluisen en bruggen.',
                active_until='01-01-2050'
            )


def parse_cctv_camera_verkeersmanagement(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the cctv camera verkeersmanagement data list of dictionaries into
    SensorData objects and yield it. Yield only the sensors with Soort == TV Camera.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    personData = PersonData(
        organisation='Gemeente Amsterdam',
        email='verkeersmanagement@amsterdam.nl',
        telephone='06123456',
        website='https://acc.sensorenregister.amsterdam.nl',
        first_name='camera',
        last_name_affix='en',
        last_name='verkeersmanagement'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            properties = feature['properties']  # properties dict

            # filter only the sonsor with the TV Camera soort.
            if properties['Soort'] != 'TV Camera':
                continue

            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][0]
            longitude = geometry['coordinates'][1]

            yield SensorData(
                owner=personData,
                reference=feature['id'],
                type='Feature',
                location=LatLong(latitude=latitude, longitude=longitude),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagment in de rol van wegbeheerder.',
                privacy_declaration='https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaring-parkeren-verkeer-bouw/verkeersmanagement',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goal='Waarnemen van het verkeer.',
                active_until='01-01-2050'
            )


def parse_kentekencamera_reistijd(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the kentekencamera en reistijd data list of dictionaries into
    SensorData objects and yield it. Yield only the sensors with
    Soort == Kentekencamera, reistijd (MoCo).
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    personData = PersonData(
        organisation='Gemeente Amsterdam',
        email='kentekencamera@amsterdam.nl',
        telephone='06123456',
        website='https://acc.sensorenregister.amsterdam.nl',
        first_name='kentekencamera',
        last_name_affix='en',
        last_name='reistijd'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            properties = feature['properties']  # properties dict

            # filter only the sonsor with the Kentekencamera, reistijd (MoCo) soort.
            if properties['Soort'] != 'Kentekencamera, reistijd (MoCo)':
                continue

            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][0]
            longitude = geometry['coordinates'][1]

            # sensors_list.append(
            yield SensorData(
                owner=personData,
                reference=feature['id'],
                type='Feature',
                location=LatLong(latitude=latitude, longitude=longitude),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
                privacy_declaration='https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaring-parkeren-verkeer-bouw/reistijden-meetsysteem-privacy/',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goal='Het tellen van voertuigen en meten van doorstroming.',
                active_until='01-01-2050'
            )


def parse_kkentekencamera_milieuzone(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the kentekencamera en milieuzone data list of dictionaries into
    SensorData objects and yield it. Yield only the sensors with
    Soort == Kentekencamera, milieuzone.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    personData = PersonData(
        organisation='Gemeente Amsterdam',
        email='kentekencameramilieuzone@amsterdam.nl',
        telephone='06123456',
        website='https://acc.sensorenregister.amsterdam.nl',
        first_name='kentekencamera',
        last_name_affix='en',
        last_name='milieuzone'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            properties = feature['properties']  # properties dict

            # filter only the sonsor with the Kentekencamera, milieuzone soort.
            if properties['Soort'] != 'Kentekencamera, milieuzone':
                continue

            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][0]
            longitude = geometry['coordinates'][1]

            yield SensorData(
                owner=personData,
                reference=feature['id'],
                type='Feature',
                location=LatLong(latitude=latitude, longitude=longitude),
                contains_pi_data='Ja',
                legal_ground='Verkeersbesluiten in de rol van wegbeheerder.',
                privacy_declaration='https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/milieuzones/',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto', 'Milieu']),
                datastream='',
                observation_goal='Handhaving van verkeersbesluiten.',
                active_until='01-01-2050'
            )


def parse_ais_masten(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the ais_masten data dict into PersonData en
    SensorData objects and yield it.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    personData = PersonData(
        organisation='Gemeente Amsterdam',
        email='programmavaren@amsterdam.nl',
        telephone='06123456',
        website='https://acc.sensorenregister.amsterdam.nl',
        first_name='ais',
        last_name_affix='en',
        last_name='masten'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][0]
            longitude = geometry['coordinates'][1]
            properties = feature['properties']  # properties dict

            yield SensorData(
                owner=personData,
                reference=feature['id'],
                type='Feature',
                location=LatLong(latitude=latitude, longitude=longitude),
                contains_pi_data='Ja',
                legal_ground='In de rol van vaarwegbeheerder op basis van de binnenvaartwet.',
                privacy_declaration=properties['Privacyverklaring'],
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goal='Vaarweg management',
                active_until='01-01-2050'
            )


def parse_verkeersonderzoek_met_cameras(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the verkeersonderzoek_met_cameras data dict into PersonData en
    SensorData objects and yield it.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    personData = PersonData(
        organisation='Gemeente Amsterdam',
        email='verkeersonderzoek@amsterdam.nl',
        telephone='06123456',
        website='https://acc.sensorenregister.amsterdam.nl',
        first_name='verkeers',
        last_name_affix='en',
        last_name='onderzoek'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][0]
            longitude = geometry['coordinates'][1]
            properties = feature['properties']  # properties dict
            yield SensorData(
                owner=personData,
                reference=feature['id'],
                type='Feature',
                location=LatLong(latitude=latitude, longitude=longitude),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
                privacy_declaration=properties['Privacyverklaring'],
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goal='Tellen van voertuigen.',
                active_until='01-01-2050'
            )


def parse_beweegbare_fysieke_afsluiting(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the beweegbare_fysieke_afsluiting data dict into PersonData en
    SensorData objects and yield it.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    personData = PersonData(
        organisation='Gemeente Amsterdam',
        email='beweegbarefysiek@amsterdam.nl',
        telephone='06123456',
        website='https://acc.sensorenregister.amsterdam.nl',
        first_name='beweegbare',
        last_name_affix='en',
        last_name='afsluiting'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][0]
            longitude = geometry['coordinates'][1]
            # properties = feature['properties']  # properties dict
            yield SensorData(
                owner=personData,
                reference=feature['id'],
                type='Feature',
                location=LatLong(latitude=latitude, longitude=longitude),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
                privacy_declaration='N/A',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goal='Verstrekken van selectieve toegang.',
                active_until='01-01-2050'
            )


def delete_not_found_sendors(sensors: List[SensorData], person: PersonData) -> str:
    """takes a list of sensor data. compares their reference with the stored sensors that belong
    to the same owner. If a sensor is not found in the stored sensor, it will delete it.
    returns a string of the total deleted records"""

    # get the reference id of the apis sensors list
    api_sensor_ids = {sensor.reference for sensor in sensors}

    # get all sensors from the owner of person.email except the sensors with reference
    # in [api_sensor_ids]
    stoered_sensors = models.Device2.objects.filter(
        owner__email=person.email).exclude(
            reference__in=api_sensor_ids).delete()

    return f'del: {stoered_sensors} for owner {person.email}'
