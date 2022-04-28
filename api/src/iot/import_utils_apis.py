from collections import Counter
from typing import Dict, Generator, List, Tuple

import requests
from django.conf import settings

from iot import import_utils, models
from iot.import_utils import LatLong, PersonData, SensorData

API = 'https://maps.amsterdam.nl/open_geodata/geojson_lnglat.php?'
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
}


def import_api_data(api_names: List[str] = None) -> List[Tuple[List[Exception], int, int]]:
    """
    takes a list of the name(s) of the api as a param, calls the url that belongs to it in the
    API_MAPPER. when the data is fetched from the api, it will convert it to a dict
    and pass it to the convert_api_data together with the api_name.
    A tuple will be returned that will contain the results. The results will be a list of tuples
    for each api as follow: (err, inserts, updates)
    """
    try:
        # if the list api_names is an empty list, copy the list of all the api_names (keys)
        # from the API_MAPPER dict so the api_names will contain a list of all the api_name
        # from the API_MAPPER dictionary, else use the app_names list with the provided
        # app_names list.
        if not api_names:
            api_names = API_MAPPER.keys()

        output_list = []
        for api_name in api_names:
            api_url = API_MAPPER[api_name]  # get the url that belongs to the api.

            response = requests.get(url=api_url)
            # check if response is 200 and content type is json, if not, return
            if response.status_code != 200 or \
                    'application/json' not in response.headers["Content-Type"]:
                raise RuntimeError(f"{response.status_code} - {response.content}")

            data = response.json()  # get the content of the response as dict
            output_list.append(convert_api_data(api_name=api_name, api_data=data))
        return output_list

    except Exception as e:
        return [([e], 0, 0)]


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

    # delete sensors from the same owner that are not in the api
    delete_not_found_sensors(sensors=sensors, source=api_name)

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

    # sensors_list = []
    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            properties = feature['properties']  # properties dict

            # filter only the sonsor with the WiFi sensor soort.
            if properties['Soort'] != 'WiFi sensor':
                continue
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][1]
            longitude = geometry['coordinates'][0]

            # sensors_list.append(
            yield SensorData(
                owner=person_data,
                reference=f"wifi_sensor_crowd_management_{feature['id']}",
                type='Aanwezigheid of nabijheidsensor',
                location=LatLong(latitude=latitude, longitude=longitude),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagment in de rol van wegbeheerder.',
                privacy_declaration=adjust_url(properties['Privacyverklaring']),
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goal='Tellen van mensen.',
                active_until='01-01-2050'
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

    # sensors_list = []
    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            properties = feature['properties']  # properties dict

            # filter only the sonsor with the WiFi sensor soort.
            if properties['Soort'] not in ['Telcamera', 'Corona CMSA', '3D sensor']:
                continue
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][1]
            longitude = geometry['coordinates'][0]

            # sensors_list.append(
            yield SensorData(
                owner=person_data,
                reference=f"sensor_crowd_management_{feature['id']}",
                type='Optische / camera sensor',
                location=LatLong(latitude=latitude, longitude=longitude),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagment in de rol van wegbeheerder.',
                privacy_declaration=adjust_url(properties['Privacyverklaring']),
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

    person_data = PersonData(
        organisation='Gemeente Amsterdam',
        email='Meldingsplicht.Sensoren@amsterdam.nl',
        telephone='14020',
        website='https://www.amsterdam.nl/',
        first_name='Afdeling',
        last_name_affix='',
        last_name='stedelijkbeheer'
    )

    # sensors_list = []
    features = data['features']  # list of sensors i think for now
    if features:
        for feature in features:
            geometry = feature['geometry']  # geometry dict
            latitude = geometry['coordinates'][1]
            longitude = geometry['coordinates'][0]
            properties = feature['properties']  # properties dict

            yield SensorData(
                owner=person_data,
                reference=f"camera_brug_en_sluisbediening_{feature['id']}",
                type='Optische / camera sensor',
                location=LatLong(latitude=latitude, longitude=longitude),
                contains_pi_data='Ja',
                legal_ground='Sluisbeheerder in het kader van de woningwet 1991',
                privacy_declaration=adjust_url(properties['Privacyverklaring']),
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
                reference=f"cctv_camera_verkeersmanagement_{feature['id']}",
                type='Optische / camera sensor',
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

            # sensors_list.append(
            yield SensorData(
                owner=person_data,
                reference=f"kentekencamera_reistijd_{feature['id']}",
                type='Optische / camera sensor',
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
                reference=f"kentekencamera_milieuzone_{feature['id']}",
                type='Optische / camera sensor',
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
                reference=f"ais_masten_{feature['id']}",
                type='Optische / camera sensor',
                location=LatLong(latitude=latitude, longitude=longitude),
                contains_pi_data='Ja',
                legal_ground='In de rol van vaarwegbeheerder op basis van de binnenvaartwet.',
                privacy_declaration=adjust_url(properties['Privacyverklaring']),
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
                location=LatLong(latitude=latitude, longitude=longitude),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
                privacy_declaration=adjust_url(properties['Privacyverklaring']),
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

            yield SensorData(
                owner=person_data,
                reference=f"beweegbare_fysieke_afsluiting_{feature['id']}",
                type='Optische / camera sensor',
                location=LatLong(latitude=latitude, longitude=longitude),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
                privacy_declaration='https://www.amsterdam.nl/privacy/privacyverklaring/',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                datastream='',
                observation_goal='Verstrekken van selectieve toegang.',
                active_until='01-01-2050'
            )


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
}
