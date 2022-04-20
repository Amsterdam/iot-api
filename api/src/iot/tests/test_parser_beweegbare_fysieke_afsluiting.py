import pytest
from django.conf import settings

from iot import import_utils, import_utils_apis, models
from iot.import_utils import LatLong, PersonData, SensorData
from iot.serializers import Device2Serializer


@pytest.fixture
def api_data():  # data from beweegbare_fysieke_afsluiting api
    return {
        "type": "FeatureCollection",
        "name": "VIS_BFA",
        "features": [
            {
                "id": 11,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.939922,
                        52.373989
                    ]
                },
                "properties": {
                    "Soortcode": 183,
                    "BFA_nummer": "VO86",
                    "BFA_type": "Vezip500",
                    "Standplaats": "Verbindingsdam, Loc 24",
                    "Jaar_aanleg": 0,
                    "Venstertijden": "00.00-7.00/11.00-24.00",
                    "Toegangssysteem": "Pasje",
                    "Camera": "",
                    "Beheerorganisatie": "V&OR VIS",
                    "Bijzonderheden": "Bij calamiteiten"
                }
            }
        ]
    }


@pytest.fixture
def api_data_2():  # a second list of api data sensors
    return {
        "type": "FeatureCollection",
        "name": "VIS_BFA",
        "features": [
            {
                "id": 11,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.999999,
                        52.373989
                    ]
                },
                "properties": {
                    "Soortcode": 183,
                    "BFA_nummer": "VO86",
                    "BFA_type": "Vezip500",
                    "Standplaats": "Verbindingsdam, Loc 24",
                    "Jaar_aanleg": 0,
                    "Venstertijden": "00.00-7.00/11.00-24.00",
                    "Toegangssysteem": "Pasje",
                    "Camera": "",
                    "Beheerorganisatie": "V&OR VIS",
                    "Bijzonderheden": "Bij calamiteiten"
                }
            },
            {
                "id": 12,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.939922,
                        52.373989
                    ]
                },
                "properties": {
                    "Soortcode": 183,
                    "BFA_nummer": "VO86",
                    "BFA_type": "Vezip500",
                    "Standplaats": "Verbindingsdam, Loc 24",
                    "Jaar_aanleg": 0,
                    "Venstertijden": "00.00-7.00/11.00-24.00",
                    "Toegangssysteem": "Pasje",
                    "Camera": "",
                    "Beheerorganisatie": "V&OR VIS",
                    "Bijzonderheden": "Bij calamiteiten"
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
        last_name="asset management"
    )


@pytest.fixture
def sensor_data(person_data):
    return SensorData(
        owner=person_data,
        reference=12,
        type="Feature",
        location=LatLong(latitude=4.939922, longitude=52.373989),
        datastream='',
        observation_goal='Verstrekken van selectieve toegang.',
        themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
        contains_pi_data='Ja',
        legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
        privacy_declaration="https://www.amsterdam.nl/privacy/privacyverklaring/",
        active_until='01-01-2050'
    )


class TestApiParser:

    def test_parse_beweegbare_fysieke_afsluiting_expected_person_sensor(self, api_data):
        """
        provide a list of 1 dictionary object and expect back a sensordata
        and persondata that matches the expected data.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="Meldingsplicht.Sensoren@amsterdam.nl",
            telephone="14020",
            website="https://www.amsterdam.nl/",
            first_name="Afdeling",
            last_name_affix="",
            last_name="asset management"
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference=11,
                type="Feature",
                location=LatLong(latitude=4.939922, longitude=52.373989),
                datastream='',
                observation_goal='Verstrekken van selectieve toegang.',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
                privacy_declaration="https://www.amsterdam.nl/privacy/privacyverklaring/",
                active_until='01-01-2050'
            )
        ]
        sensor_list = list(import_utils_apis.parse_beweegbare_fysieke_afsluiting(
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
        'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
        'telephone': '14020',
        'website': 'https://www.amsterdam.nl/',
        'name': 'Afdeling asset management',
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
        'location': {'latitude': 4.939922, 'longitude': 52.373989},
        'location_description': None,
        'observation_goal': 'Verstrekken van selectieve toegang.',
        'owner': {
            'name': 'Afdeling asset management',
            'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'privacy_declaration': 'https://www.amsterdam.nl/privacy/privacyverklaring/',
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Overig',
        'reference': '11',
    }

    expected_2 = {
        'active_until': '2050-01-01',
        'contains_pi_data': True,
        'datastream': '',
        'legal_ground': 'Verkeersmanagement in de rol van wegbeheerder.',
        'location': {'latitude': 4.939922, 'longitude': 52.373989},
        'location_description': None,
        'observation_goal': 'Verstrekken van selectieve toegang.',
        'owner': {
            'name': 'Afdeling asset management',
            'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'privacy_declaration': 'https://www.amsterdam.nl/privacy/privacyverklaring/',
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Overig',
        'reference': '12',
    }

    def test_import_sensor(self, sensor_data):
        # Basic check for importing sensor data
        owner = import_utils.import_person(sensor_data.owner)
        import_utils.import_sensor(sensor_data, owner)
        assert self.actual[0] == self.expected_2

    def test_import_sensor_from_parse_beweegbare_fysieke_afsluiting_success(self, api_data):
        """
        provide a dict from the beweegbare_fysieke_afsluiting api and call
        the parser of the beweegbare_fysieke_afsluiting to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_utils_apis.parse_beweegbare_fysieke_afsluiting
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

    def test_convert_api_data_beweegbare_sensor_only_insert_2(self, api_data_2):
        """
        provide a dict from the beweegbare sensor crowd management api and the
        the name of the parser which is the api_name. Expect to have two
        sensors created and a tuple to be returned.
        """

        result = import_utils_apis.convert_api_data(
            api_name='beweegbare_fysieke_afsluiting',
            api_data=api_data_2
        )

        assert type(result) == tuple
        assert result == ([], 2, 0)
        assert len(self.actual) == 2

    def test_convert_api_data_beweegbare_sensor_1_insert_1_update(self, api_data, api_data_2):
        """
        call the convert_api function twice with two different lists of sensors.
        The second list will contain the same sensor as in the first list.
        Expect to have one sensor being updated and another one inserted.
        A tuple to be returned.
        """

        # insert the first list of sensor which should include only one sensor.
        result_1 = import_utils_apis.convert_api_data(
            api_name='beweegbare_fysieke_afsluiting',
            api_data=api_data
        )

        # insert the second list of sensor which should include two sensors.
        result_2 = import_utils_apis.convert_api_data(
            api_name='beweegbare_fysieke_afsluiting',
            api_data=api_data_2
        )

        # get the sensor with referece 2 because it should have been updated.
        sensor_ref_2 = next((sensor for sensor in self.actual if sensor['reference'] == '11'), None)

        assert result_1 == ([], 1, 0)  # confirm the first insert only inserted one record
        assert result_2 == ([], 1, 1)  # confirm one insert and one update
        assert len(self.actual) == 2
        assert sensor_ref_2['location']['latitude'] == 4.999999

    def test_convert_api_data_beweegbare_sensor_1_update_1_delete(self, api_data, api_data_2):
        """
        call the convert_api function twice with two different lists of sensors.
        The second list will not contain one of the sensors of the first list.
        Expect to have one sensor being updated and another one deleted.
        A tuple to be returned.
        """

        # insert the first list of sensor which should include two sensor.
        result_1 = import_utils_apis.convert_api_data(
            api_name='beweegbare_fysieke_afsluiting',
            api_data=api_data_2
        )

        # insert the second list of sensor which should include one sensors.
        result_2 = import_utils_apis.convert_api_data(
            api_name='beweegbare_fysieke_afsluiting',
            api_data=api_data
        )

        # get the only sensor that should have been updated.
        sensor = self.actual[0]

        assert result_1 == ([], 2, 0)  # confirm the first insert only inserted two records
        assert result_2 == ([], 0, 1)  # confirm one update only
        assert len(self.actual) == 1
        assert sensor['location']['latitude'] == 4.939922
