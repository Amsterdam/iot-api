import pytest
from django.conf import settings

from iot import import_utils, import_utils_apis, models
from iot.import_utils import LatLong, PersonData, SensorData
from iot.serializers import Device2Serializer


@pytest.fixture
def vomc_data():  # verkeersonderzoek_met_cameras
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
def migrated_data():
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
        first_name="verkeers",
        last_name_affix="",
        last_name="onderzoek"
    )


@pytest.fixture
def sensor_data(person_data):
    return SensorData(
        owner=person_data,
        reference=11,
        type="Feature",
        location=LatLong(latitude=4.9021014, longitude=52.3689078),
        datastream='',
        observation_goal='Tellen van voertuigen.',
        themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
        contains_pi_data='Ja',
        legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
        privacy_declaration="https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/artikel-3/",
        active_until='01-01-2050'
    )


class TestApiParser:

    def test_parse_verkeersonderzoek_met_cameras_expected_person_sensor(self, vomc_data):
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
            first_name="verkeers",
            last_name_affix="",
            last_name="onderzoek"
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference=10,
                type="Feature",
                location=LatLong(latitude=4.9021014, longitude=52.3689078),
                datastream='',
                observation_goal='Tellen van voertuigen.',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
                privacy_declaration="https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/artikel-3/",
                active_until='01-01-2050'
            )
        ]
        sensor_list = list(import_utils_apis.parse_verkeersonderzoek_met_cameras(
            data=vomc_data
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
        'name': 'verkeers onderzoek',
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
        'legal_ground': 'Verkeersmanagement in de rol van wegbeheerder.',
        'location': {'latitude': 4.9021014, 'longitude': 52.3689078},
        'location_description': None,
        'observation_goal': 'Tellen van voertuigen.',
        'owner': {
            'name': 'verkeers onderzoek',
            'email': 'verkeersonderzoek@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'privacy_declaration': 'https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/artikel-3/',
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Overig',  # needs to be checked why not Feature
        'reference': '10',
    }

    expected_2 = {
        'active_until': '2050-01-01',
        'contains_pi_data': True,
        'datastream': '',
        'legal_ground': 'Verkeersmanagement in de rol van wegbeheerder.',
        'location': {'latitude': 4.9021014, 'longitude': 52.3689078},
        'location_description': None,
        'observation_goal': 'Tellen van voertuigen.',
        'owner': {
            'name': 'verkeers onderzoek',
            'email': 'verkeersonderzoek@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'privacy_declaration': 'https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/artikel-3/',
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Overig',  # needs to be checked why not Feature
        'reference': '11',
    }

    def test_import_sensor(self, sensor_data):
        # Basic check for importing sensor data
        owner = import_utils.import_person(sensor_data.owner)
        import_utils.import_sensor(sensor_data, owner)
        assert self.actual[0] == self.expected_2

    def test_import_sensor_from_parse_verkeersonderzoek_met_cameras_success(self, vomc_data):
        """
        provide a dict from the verkeersonderzoek_met_cameras api and call
        the parser of the verkeersonderzoek_met_cameras to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_utils_apis.parse_verkeersonderzoek_met_cameras
        sensor_list = list(parser(vomc_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_utils.import_person(person_data=person)
        result = import_utils.import_sensor(sensor, imported_person)

        assert type(result[0]) == models.Device2  # expet a device2 object to be returned
        assert self.actual[0] == self.expected_1
