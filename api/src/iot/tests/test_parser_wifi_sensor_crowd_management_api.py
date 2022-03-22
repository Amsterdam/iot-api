import pytest
from django.conf import settings

from iot import import_utils, import_utils_apis, models
from iot.import_utils import LatLong, PersonData, SensorData
from iot.serializers import Device2Serializer


@pytest.fixture
def wscm_data():  # wifi_sensor_crowd_management
    return {
        "type": "FeatureCollection",
        "name": "CROWDSENSOREN",
        "features": [
            {
                "id": 13,
                "type": "Feature",
                "geometry":
                {
                    "type": "Point",
                    "coordinates": [
                        4.901853,
                        52.3794285
                    ]
                },
                "properties":
                {
                    "Objectnummer": "GABW-03",
                    "Soort": "Not WiFi sensor",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/foo/"
                }
            },
            {
                "id": 2,
                "type": "Feature",
                "geometry":
                {
                    "type": "Point",
                    "coordinates": [
                        4.901852,
                        52.3794284
                    ]
                },
                "properties":
                {
                    "Objectnummer": "GABW-03",
                    "Soort": "WiFi sensor",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/foo/"
                }
            },
        ]
    }


@pytest.fixture
def migrated_data():
    return {
        "type": "FeatureCollection",
        "name": "CROWDSENSOREN",
        "features": [
            {
                "id": 2,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.99999,
                        52.3794284
                    ]
                },
                "properties": {
                    "Objectnummer": "GABW-03",
                    "Soort": "WiFi sensor",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/bar/"
                }
            },
            {
                "id": 27,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.9013573,
                        52.3794903
                    ]
                },
                "properties": {
                    "Objectnummer": "GABW-04",
                    "Soort": "WiFi sensor",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/foobar/"
                }
            }
        ]
    }


@pytest.fixture
def person_data():
    return PersonData(
        organisation="Gemeente Amsterdam",
        email="LVMA@amsterdam.nl",
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
        reference=3,
        type="Feature",
        location=LatLong(latitude=4.901852, longitude=52.3794284),
        datastream='',
        observation_goal='Tellen van mensen.',
        themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
        contains_pi_data='Ja',
        legal_ground='Verkeersmanagment in de rol van wegbeheerder.',
        privacy_declaration="https://www.amsterdam.nl/foo/",
        active_until='01-01-2050'
    )


class TestApiParser:

    def test_parse_wifi_sensor_crowd_management_expected_persondata_sensor(self, wscm_data):
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
            first_name="verkeers",
            last_name_affix="",
            last_name="onderzoek"
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference=2,
                type="Feature",
                location=LatLong(latitude=4.901852, longitude=52.3794284),
                datastream='',
                observation_goal='Tellen van mensen.',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagment in de rol van wegbeheerder.',
                privacy_declaration="https://www.amsterdam.nl/foo/",
                active_until='01-01-2050'
            )
        ]
        sensor_list = list(import_utils_apis.parse_wifi_sensor_crowd_management(data=wscm_data))
        sensor = sensor_list[0]  # expect the first and only element
        owner = sensor.owner

        assert len(sensor_list) == 1
        assert sensor == expected[0]
        assert owner == expected_owner


@pytest.mark.django_db
class TestImportPerson:

    @property
    def actual(self):
        fields = 'organisation', 'email', 'telephone', 'website', 'name'
        return list(models.Person2.objects.values(*fields).order_by('id').all())

    expected = {
        'organisation': 'Gemeente Amsterdam',
        'email': 'LVMA@amsterdam.nl',
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
        'legal_ground': 'Verkeersmanagment in de rol van wegbeheerder.',
        'location': {'latitude': 4.901852, 'longitude': 52.3794284},
        'location_description': None,
        'observation_goal': 'Tellen van mensen.',
        'owner': {
            'name': 'verkeers onderzoek',
            'email': 'LVMA@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'privacy_declaration': 'https://www.amsterdam.nl/foo/',
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Overig',  # needs to be checked why not Feature
        'reference': '2',
    }

    expected_2 = {
        'active_until': '2050-01-01',
        'contains_pi_data': True,
        'datastream': '',
        'legal_ground': 'Verkeersmanagment in de rol van wegbeheerder.',
        'location': {'latitude': 4.901852, 'longitude': 52.3794284},
        'location_description': None,
        'observation_goal': 'Tellen van mensen.',
        'owner': {
            'name': 'verkeers onderzoek',
            'email': 'LVMA@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'privacy_declaration': 'https://www.amsterdam.nl/foo/',
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Overig',  # needs to be checked why not Feature
        'reference': '3',
    }

    def test_import_sensor(self, sensor_data):
        # Basic check for importing sensor data
        owner = import_utils.import_person(sensor_data.owner)
        import_utils.import_sensor(sensor_data, owner)
        assert self.actual[0] == self.expected_2

    def test_import_sensor_from_wifi_sensor_crowd_management(self, wscm_data):
        """
        provide a dict from the wifi sensor crowd management api and call
        the parser of the wifi_sensor_crowd_management to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_utils_apis.parse_wifi_sensor_crowd_management
        sensor_list = list(parser(wscm_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_utils.import_person(person_data=person)
        result = import_utils.import_sensor(sensor, imported_person)

        assert type(result[0]) == models.Device2  # expet a device2 object to be returned
        assert self.actual[0] == self.expected_1


@pytest.mark.django_db
class TestMigrateApiData:
    """tests for the migrate_api_data function."""

    @property
    def actual(self):
        return [
            Device2Serializer(device).data
            for device in models.Device2.objects.all()
        ]

    def test_migrate_api_data_wifi_sensor_only_insert_2(self, migrated_data):
        """
        provide a dict from the wifi sensor crowd management api and the
        the name of the parser which is the api_name. Expect to have two
        sensors created and a tuple to be returned.
        """

        result = import_utils_apis.migrate_api_data(
            api_name='wifi_sensor_crowd_management',
            api_data=migrated_data
        )

        assert type(result) == tuple
        assert result == ([], 2)
        assert len(self.actual) == 2

    def test_migrate_api_data_wifi_sensor_one_insert_one_update(self, wscm_data, migrated_data):
        """
        call the migrate_api function twice with two different lists of sensors.
        The second list will contain the same sensor as in the first list.
        Expect to have one sensor being updated and another one inserted.
        A tuple to be returned.
        """

        # insert the first list of sensor which should include only one sensor.
        result_1 = import_utils_apis.migrate_api_data(
            api_name='wifi_sensor_crowd_management',
            api_data=wscm_data
        )

        # insert the second list of sensor which should include two sensors.
        result_2 = import_utils_apis.migrate_api_data(
            api_name='wifi_sensor_crowd_management',
            api_data=migrated_data
        )

        # get the sensor with referece 2 because it should have been updated.
        sensor_ref_2 = next((sensor for sensor in self.actual if sensor['reference'] == '2'), None)

        assert result_1 == ([], 1)  # confirm the first insert only inserted one record
        assert result_2 == ([], 1)  # confirm the first insert only inserted one record
        assert len(self.actual) == 2
        assert sensor_ref_2['location']['latitude'] == 4.99999

    def test_migrate_api_data_wifi_sensor_one_update_one_delete(self, wscm_data, migrated_data):
        """
        call the migrate_api function twice with two different lists of sensors.
        The second list will not contain one of the sensors of the first list.
        Expect to have one sensor being updated and another one deleted.
        A tuple to be returned.
        """

        # insert the first list of sensor which should include two sensor.
        result_1 = import_utils_apis.migrate_api_data(
            api_name='wifi_sensor_crowd_management',
            api_data=migrated_data
        )

        # insert the second list of sensor which should include one sensors.
        result_2 = import_utils_apis.migrate_api_data(
            api_name='wifi_sensor_crowd_management',
            api_data=wscm_data
        )

        # get the only sensor that should have been updated.
        sensor = self.actual[0]

        assert result_1 == ([], 2)  # confirm the first insert only inserted two records
        assert result_2 == ([], 0)  # confirm the first insert only updated so should be 0
        assert len(self.actual) == 1
        assert sensor['location']['latitude'] == 4.901852
