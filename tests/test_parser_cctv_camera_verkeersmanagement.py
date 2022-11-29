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
        "name": "VIS",
        "features": [
            {
                "id": 16,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.895861, 52.381541]},
                "properties": {
                    "Soort": "Ignore TV Camera",
                    "Soortcode": 111,
                    "Standplaats": "De Ruyterkade - Havengebouw",
                    "Bouwjaar": 2015,
                    "Voeding": "Uit havengebouw",
                    "Objectnummer_Amsterdam": "TV-117-16",
                    "Objectnummer_leverancier": "TAC64",
                    "VRI_nummer": 117,
                    "Rotatie": 0,
                },
            },
            {
                "id": 5,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.895862, 52.381543]},
                "properties": {
                    "Soort": "TV Camera",
                    "Soortcode": 111,
                    "Standplaats": "De Ruyterkade - Havengebouw",
                    "Bouwjaar": 2015,
                    "Voeding": "Uit havengebouw",
                    "Objectnummer_Amsterdam": "TV-117-5",
                    "Objectnummer_leverancier": "TAC64",
                    "VRI_nummer": 117,
                    "Rotatie": 0,
                },
            },
            {
                "id": 15,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.8958601, 52.3815401]},
                "properties": {
                    "Soort": "No TV Camera",
                    "Soortcode": 111,
                    "Standplaats": "De Ruyterkade - Havengebouw",
                    "Bouwjaar": 2015,
                    "Voeding": "Uit havengebouw",
                    "Objectnummer_Amsterdam": "TV-117-15",
                    "Objectnummer_leverancier": "TAC64",
                    "VRI_nummer": 117,
                    "Rotatie": 0,
                },
            },
        ],
    }


@pytest.fixture
def api_data_2():  # a second list of api data sensors
    return {
        "type": "FeatureCollection",
        "name": "VIS",
        "features": [
            {
                "id": 16,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.895861, 52.381541]},
                "properties": {
                    "Soort": "TV Camera",
                    "Soortcode": 111,
                    "Standplaats": "De Ruyterkade - Havengebouw",
                    "Bouwjaar": 2015,
                    "Voeding": "Uit havengebouw",
                    "Objectnummer_Amsterdam": "TV-117-16",
                    "Objectnummer_leverancier": "TAC64",
                    "VRI_nummer": 117,
                    "Rotatie": 0,
                },
            },
            {
                "id": 5,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.999999, 52.381543]},
                "properties": {
                    "Soort": "TV Camera",
                    "Soortcode": 111,
                    "Standplaats": "De Ruyterkade - Havengebouw",
                    "Bouwjaar": 2015,
                    "Voeding": "Uit havengebouw",
                    "Objectnummer_Amsterdam": "TV-117-5",
                    "Objectnummer_leverancier": "TAC64",
                    "VRI_nummer": 117,
                    "Rotatie": 0,
                },
            },
        ],
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
        last_name="verkeersmanagement",
    )


@pytest.fixture
def sensor_data(person_data):
    return SensorData(
        owner=person_data,
        reference='TV-117-6',
        type="Optische / camera sensor",
        location=Location(
            lat_long=LatLong(latitude=52.381543, longitude=4.895862),
            postcode_house_number=None,
            description='',
            regions='',
        ),
        datastream='',
        observation_goals=[
            ObservationGoal(
                observation_goal='Waarnemen van het verkeer.',
                legal_ground='Verkeersmanagment in de rol van wegbeheerder.',
                privacy_declaration="https://www.amsterdam.nl/privacy/\
specifieke/privacyverklaring-parkeren-verkeer-bouw/verkeersmanagement",
            )
        ],
        themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
        contains_pi_data='Ja',
        active_until='01-01-2050',
        projects=[''],
    )


class TestApiParser:
    def test_parse_cctv_camera_verkeersmanagement_one_person_sensor_with_filter(
        self, api_data
    ):
        """
        provide a list of three dictionaries of three sensors. only one
        sensor with the soort TV Camera should be returned.
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
            last_name="verkeersmanagement",
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference='TV-117-5',
                type="Optische / camera sensor",
                location=Location(
                    lat_long=LatLong(latitude=52.381543, longitude=4.895862),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                datastream='',
                observation_goals=[
                    ObservationGoal(
                        observation_goal='Waarnemen van het verkeer.',
                        legal_ground='Verkeersmanagment in de rol van wegbeheerder.',
                        privacy_declaration="https://www.amsterdam.nl/privacy/\
specifieke/privacyverklaring-parkeren-verkeer-bouw/verkeersmanagement",
                    )
                ],
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Ja',
                active_until='01-01-2050',
                projects=[''],
            )
        ]
        sensor_list = list(
            import_apis.parse_cctv_camera_verkeersmanagement(data=api_data)
        )
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
        return list(models.Person.objects.values(*fields).order_by('id').all())

    expected = {
        'organisation': 'Gemeente Amsterdam',
        'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
        'telephone': '14020',
        'website': 'https://www.amsterdam.nl/',
        'name': 'Afdeling verkeersmanagement',
    }

    def test_import_person(self, person_data):
        import_person.import_person(person_data)
        assert self.actual == [self.expected]


@pytest.mark.django_db
class TestImportSensor:
    @property
    def actual(self):
        return [DeviceSerializer(device).data for device in models.Device.objects.all()]

    expected_1 = {
        'active_until': '2050-01-01',
        'contains_pi_data': True,
        'datastream': '',
        'location': {'latitude': 52.381543, 'longitude': 4.895862},
        'location_description': None,
        'observation_goals': [
            {
                'observation_goal': 'Waarnemen van het verkeer.',
                'legal_ground': 'Verkeersmanagment in de rol van wegbeheerder.',
                'privacy_declaration': "https://www.amsterdam.nl/privacy/\
specifieke/privacyverklaring-parkeren-verkeer-bouw/verkeersmanagement",
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
        'reference': 'TV-117-5',
        'project_paths': [],
    }

    expected_2 = {
        'active_until': '2050-01-01',
        'contains_pi_data': True,
        'datastream': '',
        'location': {'latitude': 52.381543, 'longitude': 4.895862},
        'location_description': None,
        'observation_goals': [
            {
                'legal_ground': 'Verkeersmanagment in de rol van wegbeheerder.',
                'observation_goal': 'Waarnemen van het verkeer.',
                'privacy_declaration': "https://www.amsterdam.nl/privacy/\
specifieke/privacyverklaring-parkeren-verkeer-bouw/verkeersmanagement",
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
        'reference': 'TV-117-6',
        'project_paths': [],
    }

    def test_import_sensor(self, sensor_data):
        # Basic check for importing sensor data
        owner = import_person.import_person(sensor_data.owner)
        import_sensor.import_sensor(sensor_data, owner)
        assert self.actual[0] == self.expected_2

    def test_import_sensor_from_cctv_camera_verkeersmanagement(self, api_data):
        """
        provide a dict from the cctv camera verkeersmanagement api and call
        the parser of the parse_cctv_camera_verkeersmanagement to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_apis.parse_cctv_camera_verkeersmanagement
        sensor_list = list(parser(api_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_person.import_person(person_data=person)
        result = import_sensor.import_sensor(sensor, imported_person)

        assert type(result[0]) == models.Device  # expect a device object to be returned
        assert self.actual[0] == self.expected_1


@pytest.mark.django_db
class TestConverteApiData:
    """tests for the convert_api_datafunction."""

    @property
    def actual(self):
        return [DeviceSerializer(device).data for device in models.Device.objects.all()]

    def test_convert_api_data_cctvcv_only_insert_2(self, api_data_2):
        """
        provide a dict from the cctv sensor crowd management api and the
        the name of the parser which is the api_name. Expect to have two
        sensors created and a tuple to be returned.
        """

        result = import_apis.convert_api_data(
            api_name='cctv_camera_verkeersmanagement', api_data=api_data_2
        )

        assert result == ([], 2, 0)
        assert len(self.actual) == 2

    def test_convert_api_data_cctvcv_one_insert_one_update(self, api_data, api_data_2):
        """
        call the convert_api_datafunction twice with two different lists of sensors.
        The second list will contain the same sensor as in the first list.
        Expect to have one sensor being updated and another one inserted.
        A tuple to be returned.
        """

        # insert the first list of sensor which should include only one sensor.
        result_1 = import_apis.convert_api_data(
            api_name='cctv_camera_verkeersmanagement', api_data=api_data
        )

        # insert the second list of sensor which should include two sensors.
        result_2 = import_apis.convert_api_data(
            api_name='cctv_camera_verkeersmanagement', api_data=api_data_2
        )

        # get the sensor with referece 2 because it should have been updated.
        sensor_ref_2 = next(
            (sensor for sensor in self.actual if sensor['reference'] == 'TV-117-5'),
            None,
        )

        assert result_1 == ([], 1, 0)
        assert result_2 == ([], 1, 1)
        assert len(self.actual) == 2
        assert sensor_ref_2['location']['latitude'] == 52.381543
