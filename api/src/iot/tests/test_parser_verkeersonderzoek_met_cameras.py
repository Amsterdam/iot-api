import pytest
from django.conf import settings

from iot import import_utils, import_utils_apis, models
from iot.import_utils import LatLong, ObservationGoal, PersonData, SensorData
from iot.serializers import Device2Serializer


@pytest.fixture
def api_data():
    return {
        "type": "FeatureCollection",
        "name": "PRIVACY_OVERIG",
        "features": [
            {
                "id": 10,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.9021014,
                        52.3689078
                    ]
                },
                "properties": {
                    "Soort": "Touringcaronderzoek",
                    "Omschrijving": "Verkeersonderzoek",
                    "Privacyverklaring": "www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/artikel-3/"
                }
            }
        ]
    }


@pytest.fixture
def api_data_2():  # a second list of api data sensors
    return {
        "type": "FeatureCollection",
        "name": "PRIVACY_OVERIG",
        "features": [
            {
                "id": 10,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.999999,
                        52.3689078
                    ]
                },
                "properties": {
                    "Soort": "Touringcaronderzoek",
                    "Omschrijving": "Verkeersonderzoek",
                    "Privacyverklaring": "www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/artikel-3/"
                }
            },
            {
                "id": 11,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.9021014,
                        52.3689078
                    ]
                },
                "properties": {
                    "Soort": "Touringcaronderzoek",
                    "Omschrijving": "Verkeersonderzoek",
                    "Privacyverklaring": "www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/artikel-3/"
                }
            }
        ]
    }


@pytest.fixture
def person_data():
    return PersonData(
        organisation="Gemeente Amsterdam",
        email="verkeersonderzoek@amsterdam.nl",
        telephone="14020",
        website="https://www.amsterdam.nl/",
        first_name="Afdeling",
        last_name_affix="",
        last_name="kennis en kaders"
    )


@pytest.fixture
def sensor_data(person_data):
    return SensorData(
        owner=person_data,
        reference='verkeersonderzoek_met_cameras_11',
        type="Optische / camera sensor",
        location=LatLong(latitude=52.3689078, longitude=4.9021014),
        datastream='',
        observation_goals=[ObservationGoal(
            observation_goal='Tellen van voertuigen.',
            legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
            privacy_declaration="https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/artikel-3/",
        )],
        themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
        contains_pi_data='Ja',
        active_until='01-01-2050'
    )


class TestApiParser:

    def test_parse_verkeersonderzoek_met_cameras_expected_person_sensor(self, api_data):
        """
        provide a list of 1 dictionary object and expect back a sensordata
        and persondata that matches the expected data.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="verkeersonderzoek@amsterdam.nl",
            telephone="14020",
            website="https://www.amsterdam.nl/",
            first_name="Afdeling",
            last_name_affix="",
            last_name="kennis en kaders"
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference='verkeersonderzoek_met_cameras_10',
                type="Optische / camera sensor",
                location=LatLong(latitude=52.3689078, longitude=4.9021014),
                datastream='',
                observation_goals=[ObservationGoal(
                    observation_goal='Tellen van voertuigen.',
                    legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
                    privacy_declaration="https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/artikel-3/",
                )],

                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Ja',
                active_until='01-01-2050'
            )
        ]
        sensor_list = list(import_utils_apis.parse_verkeersonderzoek_met_cameras(
            data=api_data
        ))
        sensor_data = sensor_list[0]
        person_data = sensor_data.owner

        assert sensor_data == expected[0]
        assert person_data == expected_owner


@pytest.mark.django_db
class TestImportPerson:

    @property
    def actual(self):
        fields = 'organisation', 'email', 'telephone', 'website', 'name'
        return list(models.Person2.objects.values(*fields).order_by('id').all())

    expected = {
        'organisation': 'Gemeente Amsterdam',
        'email': 'verkeersonderzoek@amsterdam.nl',
        'telephone': '14020',
        'website': 'https://www.amsterdam.nl/',
        'name': 'Afdeling kennis en kaders',
    }

    def test_import_person(self, person_data):
        import_utils.import_person(person_data)
        assert self.actual == [self.expected]


@pytest.mark.django_db
class TestImportSensor:

    @property
    def actual(self):
        return [
            Device2Serializer(device).data
            for device in models.Device2.objects.all()
        ]

    expected_1 = {
        'active_until': '2050-01-01',
        'contains_pi_data': True,
        'datastream': '',
        'location': {'latitude': 52.3689078, 'longitude': 4.9021014},
        'location_description': None,
        'observation_goals': [
            {
                'legal_ground': 'Verkeersmanagement in de rol van wegbeheerder.',
                'observation_goal': 'Tellen van voertuigen.',
                'privacy_declaration': 'https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/artikel-3/',
            }
        ],
        'owner': {
            'name': 'Afdeling kennis en kaders',
            'email': 'verkeersonderzoek@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Optische / camera sensor',
        'reference': 'verkeersonderzoek_met_cameras_10',
    }

    expected_2 = {
        'active_until': '2050-01-01',
        'contains_pi_data': True,
        'datastream': '',
        'location': {'latitude': 52.3689078, 'longitude': 4.9021014},
        'location_description': None,
        'observation_goals': [
            {
                'legal_ground': 'Verkeersmanagement in de rol van wegbeheerder.',
                'observation_goal': 'Tellen van voertuigen.',
                'privacy_declaration': 'https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/artikel-3/',
            }
        ],
        'owner': {
            'name': 'Afdeling kennis en kaders',
            'email': 'verkeersonderzoek@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Optische / camera sensor',
        'reference': 'verkeersonderzoek_met_cameras_11',
    }

    def test_import_sensor(self, sensor_data):
        # Basic check for importing sensor data
        owner = import_utils.import_person(sensor_data.owner)
        import_utils.import_sensor(sensor_data, owner)
        assert self.actual[0] == self.expected_2

    def test_import_sensor_from_parse_verkeersonderzoek_met_cameras_success(self, api_data):
        """
        provide a dict from the verkeersonderzoek_met_cameras api and call
        the parser of the verkeersonderzoek_met_cameras to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_utils_apis.parse_verkeersonderzoek_met_cameras
        sensor_list = list(parser(api_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_utils.import_person(person_data=person)
        result = import_utils.import_sensor(sensor, imported_person)

        assert type(result[0]) == models.Device2  # expet a device2 object to be returned
        assert self.actual[0] == self.expected_1
