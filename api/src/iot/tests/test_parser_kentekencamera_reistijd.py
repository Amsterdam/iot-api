import pytest
from django.conf import settings

from iot import import_utils, import_utils_apis, models
from iot.import_utils import LatLong, ObservationGoal, PersonData, SensorData
from iot.serializers import Device2Serializer


@pytest.fixture
def api_data():
    return {
        "type": "FeatureCollection",
        "name": "VIS",
        "features": [
            {
                "id": 78,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.9999991,
                        52.0000001
                    ]
                },
                "properties": {
                    "Soort": "Wrong Kentekencamera, reistijd (MoCo)",
                    "Soortcode": 124,
                    "Standplaats": "Westerpark (s100) nabij Nassauplein (s103)",
                    "Bouwjaar": 2019,
                    "Voeding": "VRI 101",
                    "Objectnummer_Amsterdam": "ANPR-03078",
                    "Objectnummer_leverancier": "",
                    "VRI_nummer": 101,
                    "Rotatie": 0
                }
            },
            {
                "id": 77,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.9999999,
                        52.0000000
                    ]
                },
                "properties": {
                    "Soort": "No Kentekencamera, reistijd (MoCo)",
                    "Soortcode": 124,
                    "Standplaats": "Westerpark (s100) nabij Nassauplein (s103)",
                    "Bouwjaar": 2019,
                    "Voeding": "VRI 101",
                    "Objectnummer_Amsterdam": "ANPR-03077",
                    "Objectnummer_leverancier": "",
                    "VRI_nummer": 101,
                    "Rotatie": 0
                }
            },
            {
                "id": 7,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.8815420,
                        52.3851890
                    ]
                },
                "properties": {
                    "Soort": "Kentekencamera, reistijd (MoCo)",
                    "Soortcode": 124,
                    "Standplaats": "Westerpark (s100) nabij Nassauplein (s103)",
                    "Bouwjaar": 2019,
                    "Voeding": "VRI 101",
                    "Objectnummer_Amsterdam": "ANPR-03047",
                    "Objectnummer_leverancier": "",
                    "VRI_nummer": 101,
                    "Rotatie": 0
                }
            }
        ]
    }


@pytest.fixture
def api_data_2():  # a second list of api data sensors
    return {
        "type": "FeatureCollection",
        "name": "VIS",
        "features": [
            {
                "id": 77,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.3977322,
                        52.0000000
                    ]
                },
                "properties": {
                    "Soort": "Kentekencamera, reistijd (MoCo)",
                    "Soortcode": 124,
                    "Standplaats": "Westerpark (s100) nabij Nassauplein (s103)",
                    "Bouwjaar": 2019,
                    "Voeding": "VRI 101",
                    "Objectnummer_Amsterdam": "ANPR-03077",
                    "Objectnummer_leverancier": "",
                    "VRI_nummer": 101,
                    "Rotatie": 0
                }
            },
            {
                "id": 7,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.999999,
                        52.3851890
                    ]
                },
                "properties": {
                    "Soort": "Kentekencamera, reistijd (MoCo)",
                    "Soortcode": 124,
                    "Standplaats": "Westerpark (s100) nabij Nassauplein (s103)",
                    "Bouwjaar": 2019,
                    "Voeding": "VRI 101",
                    "Objectnummer_Amsterdam": "ANPR-03047",
                    "Objectnummer_leverancier": "",
                    "VRI_nummer": 101,
                    "Rotatie": 0
                }
            }
        ]
    }


@pytest.fixture
def person_data():
    return PersonData(
        organisation="Gemeente Amsterdam",
        email="Meldingsplicht.Sensoren@amsterdam.nl",
        telephone="14020",
        website="https://www.amsterdam.nl/",
        first_name="Afdeling",
        last_name_affix="",
        last_name="verkeersmanagement"
    )


@pytest.fixture
def sensor_data(person_data):
    return SensorData(
        owner=person_data,
        reference='ANPR-03048',
        type="Optische / camera sensor",
        location=LatLong(latitude=52.3851890, longitude=4.88154200),
        datastream='',
        observation_goals=[ObservationGoal(
            observation_goal='Het tellen van voertuigen en meten van doorstroming.',
            legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
            privacy_declaration="https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaring-parkeren-verkeer-bouw/reistijden-meetsysteem-privacy/",
        )],
        themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
        contains_pi_data='Ja',
        active_until='01-01-2050'
    )


class TestApiParser:

    def test_parse_kentekencamera_reistijd_expected_person_sensor_with_filter(self, api_data):
        """
        provide a list of three dictionaries of three sensors. only one
        sensor with the soort Kentekencamera, reistijd (MoCo) should be returned.
        The sensor and the owner should match the expected data.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="Meldingsplicht.Sensoren@amsterdam.nl",
            telephone="14020",
            website="https://www.amsterdam.nl/",
            first_name="Afdeling",
            last_name_affix="",
            last_name="verkeersmanagement"
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference='ANPR-03047',
                type="Optische / camera sensor",
                location=LatLong(latitude=52.3851890, longitude=4.88154200),
                datastream='',
                observation_goals=[ObservationGoal(
                    observation_goal='Het tellen van voertuigen en meten van doorstroming.',
                    legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
                    privacy_declaration="https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaring-parkeren-verkeer-bouw/reistijden-meetsysteem-privacy/",
                )],
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Ja',
                active_until='01-01-2050'
            )
        ]
        sensor_list = list(import_utils_apis.parse_kentekencamera_reistijd(data=api_data))
        sensor_data = sensor_list[0]
        person_data = sensor_data.owner

        assert len(sensor_list) == 1
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
        'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
        'telephone': '14020',
        'website': 'https://www.amsterdam.nl/',
        'name': 'Afdeling verkeersmanagement',
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
        'location': {'latitude': 52.3851890, 'longitude': 4.8815420},
        'location_description': None,
        'observation_goals': [
            {
                'observation_goal': 'Het tellen van voertuigen en meten van doorstroming.',
                'legal_ground': 'Verkeersmanagement in de rol van wegbeheerder.',
                'privacy_declaration': "https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaring-parkeren-verkeer-bouw/reistijden-meetsysteem-privacy/",
            }
        ],

        'owner': {
            'name': 'Afdeling verkeersmanagement',
            'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },

        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Optische / camera sensor',
        'reference': 'ANPR-03047',
    }

    expected_2 = {
        'active_until': '2050-01-01',
        'contains_pi_data': True,
        'datastream': '',
        'location': {'latitude': 52.3851890, 'longitude': 4.8815420},
        'location_description': None,
        'observation_goals': [
            {
                'legal_ground': 'Verkeersmanagement in de rol van wegbeheerder.',
                'observation_goal': 'Het tellen van voertuigen en meten van doorstroming.',
                'privacy_declaration': "https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaring-parkeren-verkeer-bouw/reistijden-meetsysteem-privacy/",
            }
        ],
        'owner': {
            'name': 'Afdeling verkeersmanagement',
            'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Optische / camera sensor',
        'reference': 'ANPR-03048',
    }

    def test_import_sensor(self, sensor_data):
        # Basic check for importing sensor data
        owner = import_utils.import_person(sensor_data.owner)
        import_utils.import_sensor(sensor_data, owner)
        assert self.actual[0] == self.expected_2

    def test_import_sensor_from_parse_kentekencamera_reistijd_success(self, api_data):
        """
        provide a dict from the kentekencamera_reistijd api and call
        the parser of the kentekencamera_reistijd to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_utils_apis.parse_kentekencamera_reistijd
        sensor_list = list(parser(api_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_utils.import_person(person_data=person)
        result = import_utils.import_sensor(sensor, imported_person)

        assert type(result[0]) == models.Device2  # expet a device2 object to be returned
        assert self.actual[0] == self.expected_1


@pytest.mark.django_db
class TestConvertApiData:
    """tests for the convert_api_data function."""

    @property
    def actual(self):
        return [
            Device2Serializer(device).data
            for device in models.Device2.objects.all()
        ]

    def test_convert_api_data_kentekencamera_reistijd_only_insert_2(self, api_data_2):
        """
        provide a dict from the kenteken sensor crowd management api and the
        the name of the parser which is the api_name. Expect to have two
        sensors created and a tuple to be returned.
        """

        result = import_utils_apis.convert_api_data(
            api_name='kentekencamera_reistijd',
            api_data=api_data_2
        )

        assert result == ([], 2, 0)
        assert len(self.actual) == 2

    def test_convert_api_data_kenteken_reistijd_1_insert_1_update(self, api_data, api_data_2):
        """
        call the convert_api function twice with two different lists of sensors.
        The second list will contain the same sensor as in the first list.
        Expect to have one sensor being updated and another one inserted.
        A tuple to be returned.
        """

        # insert the first list of sensor which should include only one sensor.
        result_1 = import_utils_apis.convert_api_data(
            api_name='kentekencamera_reistijd',
            api_data=api_data
        )

        # insert the second list of sensor which should include two sensors.
        result_2 = import_utils_apis.convert_api_data(
            api_name='kentekencamera_reistijd',
            api_data=api_data_2
        )

        # get the sensor with referece 7 because it should have been updated.
        sensor_ref_2 = next((sensor for sensor in self.actual if
                             sensor['reference'] == 'ANPR-03047'), None)

        assert result_1 == ([], 1, 0)
        assert result_2 == ([], 1, 1)
        assert len(self.actual) == 2
        assert sensor_ref_2['location']['longitude'] == 4.999999

    @pytest.mark.skip()
    def test_convert_api_data_kenteken_reistijd_1_update_1_delete(self, api_data, api_data_2):
        """
        call the convert_api function twice with two different lists of sensors.
        The second list will not contain one of the sensors of the first list.
        Expect to have one sensor being updated and another one deleted.
        A tuple to be returned.
        """

        # insert the first list of sensor which should include two sensor.
        result_1 = import_utils_apis.convert_api_data(
            api_name='kentekencamera_reistijd',
            api_data=api_data_2
        )

        # insert the second list of sensor which should include one sensors.
        result_2 = import_utils_apis.convert_api_data(
            api_name='kentekencamera_reistijd',
            api_data=api_data
        )

        # get the only sensor that should have been updated.
        sensor = self.actual[0]

        assert result_1 == ([], 2, 0)
        assert result_2 == ([], 0, 1)
        assert len(self.actual) == 1
        assert sensor['location']['longitude'] == 4.881542
