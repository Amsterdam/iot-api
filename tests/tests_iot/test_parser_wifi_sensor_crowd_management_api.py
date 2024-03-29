import json

import pytest
from django.conf import settings

from iot import models
from iot.dateclasses import LatLong, Location, ObservationGoal, PersonData, SensorData
from iot.importers import import_apis, import_person, import_sensor
from iot.serializers import DeviceSerializer


@pytest.fixture
def api_data():
    return {
        "type": "FeatureCollection",
        "name": "CROWDSENSOREN",
        "features": [
            {
                "id": 13,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.901853, 52.3794285]},
                "properties": {
                    "Objectnummer": "GABW-01",
                    "Soort": "Not WiFi sensor",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/foo/",
                },
            },
            {
                "id": 2,
                "type": "Feuture",
                "geometry": {"type": "Point", "coordinates": [4.901852, 52.3794284]},
                "properties": {
                    "Objectnummer": "GABW-03",
                    "Soort": "WiFi sensor",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/foo/",
                },
            },
        ],
    }


@pytest.fixture
def api_data_2():  # a second list of api data sensors
    return {
        "type": "FeatureCollection",
        "name": "CROWDSENSOREN",
        "features": [
            {
                "id": 2,
                "type": "Feuture",
                "geometry": {"type": "Point", "coordinates": [4.99999, 52.3794284]},
                "properties": {
                    "Objectnummer": "GABW-03",
                    "Soort": "WiFi sensor",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/bar/",
                },
            },
            {
                "id": 27,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.9013573, 52.3794903]},
                "properties": {
                    "Objectnummer": "GABW-04",
                    "Soort": "WiFi sensor",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/foobar/",
                },
            },
        ],
    }


@pytest.fixture
def person_data():
    return PersonData(
        organisation="Gemeente Amsterdam",
        email="LVMA@amsterdam.nl",
        telephone="14020",
        website="https://www.amsterdam.nl/",
        name="Afdeling verkeersmanagment",
    )


@pytest.fixture
def sensor_data(person_data):
    return SensorData(
        owner=person_data,
        reference='GABW-05',
        type="Aanwezigheid of nabijheidsensor",
        location=Location(
            lat_long=LatLong(latitude=52.3794284, longitude=4.901852),
            postcode_house_number=None,
            description='',
            regions='',
        ),
        datastream='',
        observation_goals=[
            ObservationGoal(
                observation_goal='Tellen van mensen.',
                privacy_declaration='https://www.amsterdam.nl/foo/',
                legal_ground='Verkeersmanagment in de rol van wegbeheerder.',
            )
        ],
        themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
        contains_pi_data='Ja',
        active_until='01-01-2050',
        projects=[''],
    )


class TestApiParser:
    def test_parse_wifi_sensor_crowd_management_expected_persondata_sensor(
        self, api_data
    ):
        """
        provide a dict object with a list of sensoren from the wifi sonso crowd management api.
        The sensors list will contain two sensor with different Soort attribute. Expect
        to get back one sensor only and the person is the expected one.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="LVMA@amsterdam.nl",
            telephone="14020",
            website="https://www.amsterdam.nl/",
            name="Afdeling verkeersmanagment",
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference='GABW-03',
                type="Aanwezigheid of nabijheidsensor",
                location=Location(
                    lat_long=LatLong(latitude=52.3794284, longitude=4.901852),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                datastream='',
                observation_goals=[
                    ObservationGoal(
                        observation_goal='Tellen van mensen.',
                        legal_ground='Verkeersmanagment in de rol van wegbeheerder.',
                        privacy_declaration="https://www.amsterdam.nl/foo/",
                    )
                ],
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Ja',
                active_until='01-01-2050',
                projects=[''],
            )
        ]
        sensor_list = list(
            import_apis.parse_wifi_sensor_crowd_management(data=api_data)
        )

        assert len(sensor_list) == 1

        sensor = sensor_list[0]  # expect the first and only element
        owner = sensor.owner

        assert sensor == expected[0]
        assert owner == expected_owner


@pytest.mark.django_db
class TestImportPerson:
    @property
    def actual(self):
        fields = 'organisation', 'email', 'telephone', 'website', 'name'
        return list(models.Person.objects.values(*fields).order_by('id').all())

    expected = {
        'organisation': 'Gemeente Amsterdam',
        'email': 'LVMA@amsterdam.nl',
        'telephone': '14020',
        'website': 'https://www.amsterdam.nl/',
        'name': 'Afdeling verkeersmanagment',
    }

    def test_import_person(self, person_data):
        import_person.import_person(person_data)
        assert self.actual == [self.expected]


@pytest.mark.django_db
class TestImportSensor:
    @property
    def actual(self):
        return [
            json.loads(json.dumps(DeviceSerializer(device).data))
            for device in models.Device.objects.all()
        ]

    expected_1 = {
        'active_until': '2050-01-01',
        'contains_pi_data': True,
        'datastream': '',
        'location': {'latitude': 52.3794284, 'longitude': 4.901852},
        'location_description': None,
        'observation_goals': [
            {
                'observation_goal': 'Tellen van mensen.',
                'privacy_declaration': 'https://www.amsterdam.nl/foo/',
                'legal_ground': 'Verkeersmanagment in de rol van wegbeheerder.',
            }
        ],
        'owner': {
            'name': 'Afdeling verkeersmanagment',
            'email': 'LVMA@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
            'telephone': '14020',
            'website': 'https://www.amsterdam.nl/',
        },
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Aanwezigheid of nabijheidsensor',
        'reference': 'GABW-03',
        'project_paths': [],
    }

    expected_2 = {
        'active_until': '2050-01-01',
        'contains_pi_data': True,
        'datastream': '',
        'location': {'latitude': 52.3794284, 'longitude': 4.901852},
        'location_description': None,
        'observation_goals': [
            {
                'observation_goal': 'Tellen van mensen.',
                'privacy_declaration': 'https://www.amsterdam.nl/foo/',
                'legal_ground': 'Verkeersmanagment in de rol van wegbeheerder.',
            }
        ],
        'owner': {
            'name': 'Afdeling verkeersmanagment',
            'email': 'LVMA@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
            'telephone': '14020',
            'website': 'https://www.amsterdam.nl/',
        },
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Aanwezigheid of nabijheidsensor',
        'reference': 'GABW-05',
        'project_paths': [],
    }

    def test_import_sensor(self, sensor_data):
        # Basic check for importing sensor data
        owner = import_person.import_person(sensor_data.owner)
        import_sensor.import_sensor(sensor_data, owner)
        assert self.actual[0] == self.expected_2

    def test_import_sensor_from_wifi_sensor_crowd_management(self, api_data):
        """
        provide a dict from the wifi sensor crowd management api and call
        the parser of the wifi_sensor_crowd_management to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_apis.parse_wifi_sensor_crowd_management
        sensor_list = list(parser(api_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_person.import_person(person_data=person)
        result = import_sensor.import_sensor(sensor, imported_person)

        assert type(result[0]) == models.Device  # expect a device object to be returned
        assert self.actual[0] == self.expected_1


@pytest.mark.django_db
class TestConvertApiData:
    """tests for the convert_api_data function."""

    @property
    def actual(self):
        return [
            json.loads(json.dumps(DeviceSerializer(device).data))
            for device in models.Device.objects.all()
        ]

    def test_convert_api_data_wifi_sensor_only_insert_2(self, api_data_2):
        """
        provide a dict from the wifi sensor crowd management api and the
        the name of the parser which is the api_name. Expect to have two
        sensors created and a tuple to be returned.
        """

        result = import_apis.convert_api_data(
            api_name='wifi_sensor_crowd_management', api_data=api_data_2
        )

        assert result == ([], 2, 0)
        assert len(self.actual) == 2

    def test_convert_api_data_wifi_sensor_one_insert_one_update(
        self, api_data, api_data_2
    ):
        """
        call the convert_api function twice with two different lists of sensors.
        The second list will contain the same sensor as in the first list.
        Expect to have one sensor being updated and another one inserted.
        A tuple to be returned.
        """

        # insert the first list of sensor which should include only one sensor.
        result_1 = import_apis.convert_api_data(
            api_name='wifi_sensor_crowd_management', api_data=api_data
        )

        # insert the second list of sensor which should include two sensors.
        result_2 = import_apis.convert_api_data(
            api_name='wifi_sensor_crowd_management', api_data=api_data_2
        )

        # get the sensor with referece 2 because it should have been updated.
        sensor_ref_2 = next(
            (sensor for sensor in self.actual if sensor['reference'] == 'GABW-03'), None
        )

        assert result_1 == ([], 1, 0)
        assert result_2 == ([], 1, 1)
        assert len(self.actual) == 2
        assert sensor_ref_2['location']['longitude'] == 4.99999
