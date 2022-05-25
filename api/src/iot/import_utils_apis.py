from collections import Counter
from typing import Dict, Generator, List, Tuple

from django.conf import settings

from iot import import_utils, models
from iot.import_utils import (LatLong, Location, ObservationGoal, PersonData,
                              SensorData)

API = 'https://maps.amsterdam.nl/open_geodata/geojson_lnglat.php?'
API_ANPR = 'https://service.vorin-amsterdam.nl/camera-geo_2/camera/geo'

API_MAPPER = {
    'wifi_sensor_crowd_management': f'{API}KAARTLAAG=CROWDSENSOREN&THEMA=cmsa',
    'sensor_crowd_management': f'{API}KAARTLAAG=CROWDSENSOREN&THEMA=cmsa',
    'camera_brug_en_sluisbediening': f'{API}KAARTLAAG=PRIVACY_BRUGSLUIS&THEMA=privacy',
    'cctv_camera_verkeersmanagement': f'{API}KAARTLAAG=VIS&THEMA=vis',
    'kentekencamera_reistijd': f'{API}KAARTLAAG=VIS&THEMA=vis',
    'kentekencamera_milieuzone': f'{API}KAARTLAAG=VIS&THEMA=vis',
    'ais_masten': f'{API}KAARTLAAG=PRIVACY_AISMASTEN&THEMA=privacy',
    'verkeersonderzoek_met_cameras': f'{API}KAARTLAAG=PRIVACY_OVERIG&THEMA=privacy',
    'beweegbare_fysieke_afsluiting': f'{API}KAARTLAAG=VIS_BFA&THEMA=vis',
    'anpr': f'{API_ANPR}'
}


def convert_api_data(api_name: str, api_data: dict) -> Tuple[List[Exception], int, int]:
    """
    takes the api_name to find the parser, and the api_data to convert the data with the
    existing data. The parser will return a generator of SensorData.
    from the generator, use the import_person_data and import_senso_data.
    It will return a tuple of a list of errors, number of insertions, number of updated
    records.
    """
    parser = PARSERS_MAPPER[api_name]

    sensors = list(parser(api_data))
    owners_list = [sensor.owner for sensor in sensors]

    for owner in owners_list:
        owner.validate()

    imported_owners = {
        person_data.email.lower(): import_utils.import_person(person_data)
        for person_data in owners_list
    }

    counter = Counter()

    errors: List[Exception] = []
    for sensor_data in sensors:
        try:
            import_utils.validate_sensor(sensor_data)
            owner = imported_owners[sensor_data.owner.email.lower()]
            _, created = import_utils.import_sensor(sensor_data, owner)
            counter.update([created])
        except Exception as e:
            errors.append(e)

    # TODO: need to create something unique for each sensor source
    # delete sensors from the same owner that are not in the api
    # delete_not_found_sensors(sensors=sensors, source=api_name)

    return (errors, counter[True], counter[False])


def parse_wifi_sensor_crowd_management(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the crowd management data list of dictionaries into SensorData objects and
    yield it. Yield only the sensors with Soort == WiFi sensor.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    person_data = PersonData(
        organisation='Gemeente Amsterdam',
        email='LVMA@amsterdam.nl',
        telephone='14020',
        website='https://www.amsterdam.nl/',
        first_name='Afdeling',
        last_name_affix='',
        last_name='verkeersmanagment'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            properties = feature['properties']  # properties dict

            # exclude any sensor with no WiFi sensor soort.
            if properties['Soort'] != 'WiFi sensor':
                continue
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][1]
            longitude = geometry['coordinates'][0]

            yield SensorData(
                owner=person_data,
                reference=properties['Objectnummer'],
                type='Aanwezigheid of nabijheidsensor',
                location=Location(
                    lat_long=LatLong(latitude=latitude, longitude=longitude),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                contains_pi_data='Ja',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goals=[ObservationGoal(
                    observation_goal='Tellen van mensen.',
                    legal_ground='Verkeersmanagment in de rol van wegbeheerder.',
                    privacy_declaration=adjust_url(properties['Privacyverklaring']),
                )],
                active_until='01-01-2050',
                projects=[]
            )


def parse_sensor_crowd_management(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the crowd management data list of dictionaries into SensorData objects and
    yield it. Yield only the sensors with Soort == WiFi sensor.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    person_data = PersonData(
        organisation='Gemeente Amsterdam',
        email='LVMA@amsterdam.nl',
        telephone='14020',
        website='https://www.amsterdam.nl/',
        first_name='Afdeling',
        last_name_affix='',
        last_name='verkeersmanagment'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            properties = feature['properties']  # properties dict

            # filter only the sonsor Telcamera, Corona CMSA, 3D sensor soort.
            if properties['Soort'] not in ['Telcamera', 'Corona CMSA', '3D sensor']:
                continue
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][1]
            longitude = geometry['coordinates'][0]

            yield SensorData(
                owner=person_data,
                reference=properties['Objectnummer'],
                type='Optische / camera sensor',
                location=Location(
                    lat_long=LatLong(latitude=latitude, longitude=longitude),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                contains_pi_data='Ja',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goals=[ObservationGoal(
                    observation_goal='Tellen van mensen.',
                    privacy_declaration=adjust_url(properties['Privacyverklaring']),
                    legal_ground='Verkeersmanagment in de rol van wegbeheerder.'
                )],
                active_until='01-01-2050',
                projects=[]
            )


def parse_camera_brug_en_sluisbediening(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the camera brug en sluisbediening data list of dictionaries into SensorData objects and
    yield it.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    person_data = PersonData(
        organisation='Gemeente Amsterdam',
        email='Meldingsplicht.Sensoren@amsterdam.nl',
        telephone='14020',
        website='https://www.amsterdam.nl/',
        first_name='Afdeling',
        last_name_affix='',
        last_name='stedelijkbeheer'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][1]
            longitude = geometry['coordinates'][0]
            properties = feature['properties']  # properties dict

            yield SensorData(
                owner=person_data,
                reference=properties['BrugSluisNummer'],
                type='Optische / camera sensor',
                location=Location(
                    lat_long=LatLong(latitude=latitude, longitude=longitude),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                contains_pi_data='Ja',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goals=[ObservationGoal(
                    observation_goal='Het bedienen van sluisen en bruggen.',
                    privacy_declaration=adjust_url(properties['Privacyverklaring']),
                    legal_ground='Sluisbeheerder in het kader van de woningwet 1991'
                )],
                active_until='01-01-2050',
                projects=[]
            )


def parse_cctv_camera_verkeersmanagement(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the cctv camera verkeersmanagement data list of dictionaries into
    SensorData objects and yield it. Yield only the sensors with Soort == TV Camera.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    person_data = PersonData(
        organisation='Gemeente Amsterdam',
        email='Meldingsplicht.Sensoren@amsterdam.nl',
        telephone='14020',
        website='https://www.amsterdam.nl/',
        first_name='Afdeling',
        last_name_affix='',
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
            latitude = geometry['coordinates'][1]
            longitude = geometry['coordinates'][0]

            yield SensorData(
                owner=person_data,
                reference=properties['Objectnummer_Amsterdam'],
                type='Optische / camera sensor',
                location=Location(
                    lat_long=LatLong(latitude=latitude, longitude=longitude),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                contains_pi_data='Ja',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goals=[ObservationGoal(
                    observation_goal='Waarnemen van het verkeer.',
                    privacy_declaration='https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaring-parkeren-verkeer-bouw/verkeersmanagement',
                    legal_ground='Verkeersmanagment in de rol van wegbeheerder.'
                )],
                active_until='01-01-2050',
                projects=[]
            )


def parse_kentekencamera_reistijd(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the kentekencamera en reistijd data list of dictionaries into
    SensorData objects and yield it. Yield only the sensors with
    Soort == Kentekencamera, reistijd (MoCo).
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    person_data = PersonData(
        organisation='Gemeente Amsterdam',
        email='Meldingsplicht.Sensoren@amsterdam.nl',
        telephone='14020',
        website='https://www.amsterdam.nl/',
        first_name='Afdeling',
        last_name_affix='',
        last_name='verkeersmanagement'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            properties = feature['properties']  # properties dict

            # filter only the sonsor with the Kentekencamera, reistijd (MoCo) soort.
            if properties['Soort'] != 'Kentekencamera, reistijd (MoCo)':
                continue

            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][1]
            longitude = geometry['coordinates'][0]

            yield SensorData(
                owner=person_data,
                reference=properties['Objectnummer_Amsterdam'],
                type='Optische / camera sensor',
                location=Location(
                    lat_long=LatLong(latitude=latitude, longitude=longitude),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                contains_pi_data='Ja',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goals=[ObservationGoal(
                    observation_goal='Het tellen van voertuigen en meten van doorstroming.',
                    privacy_declaration='https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaring-parkeren-verkeer-bouw/reistijden-meetsysteem-privacy/',
                    legal_ground='Verkeersmanagement in de rol van wegbeheerder.'
                )],
                active_until='01-01-2050',
                projects=[]
            )


def parse_kentekencamera_milieuzone(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the kentekencamera en milieuzone data list of dictionaries into
    SensorData objects and yield it. Yield only the sensors with
    Soort == Kentekencamera, milieuzone.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    person_data = PersonData(
        organisation='Gemeente Amsterdam',
        email='Meldingsplicht.Sensoren@amsterdam.nl',
        telephone='14020',
        website='https://www.amsterdam.nl/',
        first_name='Afdeling',
        last_name_affix='',
        last_name='stedelijk beheer'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            properties = feature['properties']  # properties dict

            # filter only the sonsor with the Kentekencamera, milieuzone soort.
            if properties['Soort'] != 'Kentekencamera, milieuzone':
                continue

            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][1]
            longitude = geometry['coordinates'][0]

            yield SensorData(
                owner=person_data,
                reference=properties['Objectnummer_Amsterdam'],
                type='Optische / camera sensor',
                location=Location(
                    lat_long=LatLong(latitude=latitude, longitude=longitude),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                contains_pi_data='Ja',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto', 'Milieu']),
                datastream='',
                observation_goals=[ObservationGoal(
                    observation_goal='Handhaving van verkeersbesluiten.',
                    privacy_declaration='https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/milieuzones/',
                    legal_ground='Verkeersbesluiten in de rol van wegbeheerder.'
                )],
                active_until='01-01-2050',
                projects=[]
            )


def parse_ais_masten(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the ais_masten data dict into PersonData en
    SensorData objects and yield it.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    person_data = PersonData(
        organisation='Gemeente Amsterdam',
        email='Meldingsplicht.Sensoren@amsterdam.nl',
        telephone='14020',
        website='https://www.amsterdam.nl/',
        first_name='Programma',
        last_name_affix='',
        last_name='varen'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][1]
            longitude = geometry['coordinates'][0]
            properties = feature['properties']  # properties dict

            yield SensorData(
                owner=person_data,
                reference=properties['Locatienaam'],
                type='Optische / camera sensor',
                location=Location(
                    lat_long=LatLong(latitude=latitude, longitude=longitude),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                contains_pi_data='Ja',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goals=[ObservationGoal(
                    observation_goal='Vaarweg management',
                    privacy_declaration=adjust_url(properties['Privacyverklaring']),
                    legal_ground='In de rol van vaarwegbeheerder op basis van de binnenvaartwet.'
                )],
                active_until='01-01-2050',
                projects=[]
            )


def parse_verkeersonderzoek_met_cameras(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the verkeersonderzoek_met_cameras data dict into PersonData en
    SensorData objects and yield it.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    person_data = PersonData(
        organisation='Gemeente Amsterdam',
        email='verkeersonderzoek@amsterdam.nl',
        telephone='14020',
        website='https://www.amsterdam.nl/',
        first_name='Afdeling',
        last_name_affix='',
        last_name='kennis en kaders'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][1]
            longitude = geometry['coordinates'][0]
            properties = feature['properties']  # properties dict

            # if the privacy_declaration url empty, skip the sensor.
            if not properties['Privacyverklaring'].strip():
                continue

            yield SensorData(
                owner=person_data,
                reference=f"verkeersonderzoek_met_cameras_{feature['id']}",
                type='Optische / camera sensor',
                location=Location(
                    lat_long=LatLong(latitude=latitude, longitude=longitude),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                contains_pi_data='Ja',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goals=[ObservationGoal(
                    observation_goal='Tellen van voertuigen.',
                    privacy_declaration=adjust_url(properties['Privacyverklaring']),
                    legal_ground='Verkeersmanagement in de rol van wegbeheerder.'
                )],
                active_until='01-01-2050',
                projects=[]
            )


def parse_beweegbare_fysieke_afsluiting(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the beweegbare_fysieke_afsluiting data dict into PersonData en
    SensorData objects and yield it.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    person_data = PersonData(
        organisation='Gemeente Amsterdam',
        email='Meldingsplicht.Sensoren@amsterdam.nl',
        telephone='14020',
        website='https://www.amsterdam.nl/',
        first_name='Afdeling',
        last_name_affix='',
        last_name='asset management'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][1]
            longitude = geometry['coordinates'][0]
            properties = feature['properties']  # properties dict

            yield SensorData(
                owner=person_data,
                reference=properties['BFA_nummer'],
                type='Optische / camera sensor',
                location=Location(
                    lat_long=LatLong(latitude=latitude, longitude=longitude),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                contains_pi_data='Ja',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goals=[ObservationGoal(
                    observation_goal='Verstrekken van selectieve toegang.',
                    privacy_declaration='https://www.amsterdam.nl/privacy/privacyverklaring/',
                    legal_ground='Verkeersmanagement in de rol van wegbeheerder.'
                )],
                active_until='01-01-2050',
                projects=[]
            )


def parse_anpr(data: dict) -> Generator[SensorData, None, None]:
    """
    convert the anpr data dict into PersonData en
    SensorData objects and yield it.
    """
    # create the personData from static defined data because the api doesn't provide
    # all the required fields

    person_data = PersonData(
        organisation='Gemeente Amsterdam',
        email='Meldingsplicht.Sensoren@amsterdam.nl',
        telephone='14020',
        website='https://www.amsterdam.nl/',
        first_name='Afdeling',
        last_name_affix='',
        last_name='anpr management'
    )

    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][1]
            longitude = geometry['coordinates'][0]
            properties = feature['properties']  # properties dict
            goals = properties['doel']  # a list of goals

            yield SensorData(
                owner=person_data,
                reference=properties['id'],
                type='Optische / camera sensor',
                location=Location(
                    lat_long=LatLong(latitude=latitude, longitude=longitude),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                contains_pi_data='Nee',  # api has no contains_pi_data
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goals=[ObservationGoal(
                    observation_goal=goal,
                    privacy_declaration='https://www.amsterdam.nl/privacy/privacyverklaring/',
                    legal_ground=None  # can be None because api has no contains_pi_data
                ) for goal in goals],
                active_until='01-01-2050',
                projects=[]
            )


# TODO: need to be adjusted with a unique value per source.
def delete_not_found_sensors(sensors: List[SensorData], source: str) -> Tuple[int, Dict[str, int]]:
    """takes a list of sensor data. with the source. compares their
    reference with the stored sensors that belong to the same owner (by source).
    If a sensor is not found in the stored sensor, it will delete it.
    returns a tuple with the number of deleted records and sensors"""

    # get the reference id of the apis sensors list
    api_sensor_ids = {sensor.reference for sensor in sensors}

    # get all sensors that start with the source except the sensors with reference
    # in [api_sensor_ids] and delete them.
    deleted_sensors = models.Device2.objects.filter(
        reference__startswith=source).exclude(
            reference__in=api_sensor_ids).delete()

    return deleted_sensors


def adjust_url(url: str) -> str:
    """If the url of the privacy_declaration doesn't start with https, the
    sensor will not be created. This function will check the provided url if
    it starts with https://. it will append https:// and return it if not found.
    """

    return url.strip() if url.startswith('https://') else f"https://{url.strip()}"


PARSERS_MAPPER = {
    'wifi_sensor_crowd_management': parse_wifi_sensor_crowd_management,
    'sensor_crowd_management': parse_sensor_crowd_management,
    'camera_brug_en_sluisbediening': parse_camera_brug_en_sluisbediening,
    'cctv_camera_verkeersmanagement': parse_cctv_camera_verkeersmanagement,
    'kentekencamera_reistijd': parse_kentekencamera_reistijd,
    'kentekencamera_milieuzone': parse_kentekencamera_milieuzone,
    'ais_masten': parse_ais_masten,
    'verkeersonderzoek_met_cameras': parse_verkeersonderzoek_met_cameras,
    'beweegbare_fysieke_afsluiting': parse_beweegbare_fysieke_afsluiting,
    'anpr': parse_anpr,
}
