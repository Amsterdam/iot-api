import pytest
from django.conf import settings

from iot import import_utils, import_utils_apis, models
from iot.import_utils import LatLong, Location, ObservationGoal, PersonData, SensorData
from iot.serializers import Device2Serializer


@pytest.fixture
def api_data():
    return {
        "type": "FeatureCollection",
        "id": "CameraCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.918723, 52.389397]},
                "properties": {
                    "type": "camera",
                    "id": "ANPR-00001-V",
                    "doel": [
                        "verkeershandhaving_milieuzone",
                        "verkeershandhaving_snorfietsrijbaan",
                    ],
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.915874, 52.34528],
                },
                "properties": {
                    "type": "camera",
                    "id": "ANPR-00002-V",
                    "doel": [
                        "verkeershandhaving_milieuzone",
                        "verkeershandhaving_snorfietsrijbaan",
                    ],
                },
            },
        ],
    }


@pytest.fixture
def api_data_2():  # a second list of api data sensors
    return {
        "type": "FeatureCollection",
        "id": "CameraCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.9999999, 52.999999]},
                "properties": {
                    "type": "camera",
                    "id": "ANPR-00001-V",
                    "doel": [
                        "verkeershandhaving_milieuzone",
                        "verkeershandhaving_snorfietsrijbaan",
                    ],
                },
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.85636, 52.37117]},
                "properties": {
                    "type": "camera",
                    "id": "ANPR-00003-V",
                    "doel": ["verkeershandhaving_milieuzone"],
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
        last_name="anpr management",
    )


@pytest.fixture
def sensor_data(person_data):
    return SensorData(
        owner=person_data,
        reference="ANPR-00004-V",
        type="Optische / camera sensor",
        location=Location(
            lat_long=LatLong(latitude=52.3794284, longitude=4.901852),
            postcode_house_number=None,
            description='',
            regions='',
        ),
        datastream="",
        observation_goals=[
            ObservationGoal(
                observation_goal="verkeershandhaving_snorfietsrijbaan",
                privacy_declaration="https://www.amsterdam.nl/privacy/privacyverklaring/",
                legal_ground=None,
            )
        ],
        themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
        contains_pi_data='Nee',
        active_until='01-01-2050',
        projects=[''],
    )


class TestApiParser:
    def test_parse_anpr_expected_persondata_sensor_objects(self, api_data):
        """
        provide a dict object with a list of sensoren from the anpr api.
        The sensors list will contain two sensor with different ids. Expect
        to get back two sensor objects and an owner.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="Meldingsplicht.Sensoren@amsterdam.nl",
            telephone="14020",
            website="https://www.amsterdam.nl/",
            first_name="Afdeling",
            last_name_affix="",
            last_name="anpr management",
        )
        # expected_value is a list of sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference="ANPR-00001-V",
                type="Optische / camera sensor",
                location=Location(
                    lat_long=LatLong(latitude=52.389397, longitude=4.918723),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                datastream='',
                observation_goals=[
                    ObservationGoal(
                        observation_goal="verkeershandhaving_milieuzone",
                        legal_ground=None,
                        privacy_declaration="https://www.amsterdam.nl/privacy/privacyverklaring/",
                    ),
                    ObservationGoal(
                        observation_goal="verkeershandhaving_snorfietsrijbaan",
                        legal_ground=None,
                        privacy_declaration="https://www.amsterdam.nl/privacy/privacyverklaring/",
                    ),
                ],
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Nee',
                active_until='01-01-2050',
                projects=[''],
            ),
            SensorData(
                owner=expected_owner,
                reference="ANPR-00002-V",
                type="Optische / camera sensor",
                location=Location(
                    lat_long=LatLong(latitude=52.34528, longitude=4.915874),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                datastream='',
                observation_goals=[
                    ObservationGoal(
                        observation_goal="verkeershandhaving_milieuzone",
                        legal_ground=None,
                        privacy_declaration="https://www.amsterdam.nl/privacy/privacyverklaring/",
                    ),
                    ObservationGoal(
                        observation_goal="verkeershandhaving_snorfietsrijbaan",
                        legal_ground=None,
                        privacy_declaration="https://www.amsterdam.nl/privacy/privacyverklaring/",
                    ),
                ],
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Nee',
                active_until='01-01-2050',
                projects=[''],
            ),
        ]
        sensors_list = list(import_utils_apis.parse_anpr(data=api_data))

        assert len(sensors_list) == 2

        owner = sensors_list[0].owner  # take the owner from one of the sensors

        assert sensors_list == expected
        assert owner == expected_owner


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
        'name': 'Afdeling anpr management',
    }

    def test_import_person(self, person_data):
        import_utils.import_person(person_data)
        assert self.actual == [self.expected]


@pytest.mark.django_db
class TestImportSensor:
    @property
    def actual(self):
        return [
            Device2Serializer(device).data for device in models.Device2.objects.all()
        ]

    expected_1 = {
        'active_until': '2050-01-01',
        'contains_pi_data': False,
        'datastream': '',
        'location': {'latitude': 52.389397, 'longitude': 4.918723},
        'location_description': None,
        'observation_goals': [
            {
                'observation_goal': 'verkeershandhaving_milieuzone',
                'privacy_declaration': 'https://www.amsterdam.nl/privacy/privacyverklaring/',
                'legal_ground': None,
            },
            {
                'observation_goal': 'verkeershandhaving_snorfietsrijbaan',
                'privacy_declaration': 'https://www.amsterdam.nl/privacy/privacyverklaring/',
                'legal_ground': None,
            },
        ],
        'owner': {
            'name': 'Afdeling anpr management',
            'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Optische / camera sensor',
        'reference': 'ANPR-00001-V',
        'project_paths': [],
    }

    expected_2 = {
        'active_until': '2050-01-01',
        'contains_pi_data': False,
        'datastream': '',
        'location': {'latitude': 52.3794284, 'longitude': 4.901852},
        'location_description': None,
        'observation_goals': [
            {
                'observation_goal': 'verkeershandhaving_snorfietsrijbaan',
                'privacy_declaration': 'https://www.amsterdam.nl/privacy/privacyverklaring/',
                'legal_ground': None,
            }
        ],
        'owner': {
            'name': 'Afdeling anpr management',
            'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Optische / camera sensor',
        'reference': 'ANPR-00004-V',
        'project_paths': [],
    }

    expected_3 = {
        'active_until': '2050-01-01',
        'contains_pi_data': False,
        'datastream': '',
        'location': {'latitude': 52.34528, 'longitude': 4.915874},
        'location_description': None,
        'observation_goals': [
            {
                'observation_goal': 'verkeershandhaving_milieuzone',
                'privacy_declaration': 'https://www.amsterdam.nl/privacy/privacyverklaring/',
                'legal_ground': None,
            },
            {
                'observation_goal': 'verkeershandhaving_snorfietsrijbaan',
                'privacy_declaration': 'https://www.amsterdam.nl/privacy/privacyverklaring/',
                'legal_ground': None,
            },
        ],
        'owner': {
            'name': 'Afdeling anpr management',
            'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Optische / camera sensor',
        'reference': 'ANPR-00002-V',
        'project_paths': [],
    }

    def test_import_sensor(self, sensor_data):
        # Basic check for importing sensor data
        owner = import_utils.import_person(sensor_data.owner)
        import_utils.import_sensor(sensor_data, owner)
        assert self.actual[0] == self.expected_2

    def test_import_sensor_from_anpr(self, api_data):
        """
        provide two sensor dictionaries from the anpr api and call
        the parser of the anpr to get two parsed sensors.
        call the import_sensor with only the second parsed sensor
        and expected it to be imported.
        """
        parser = import_utils_apis.parse_anpr
        sensors_list = list(parser(api_data))
        person = sensors_list[0].owner  # take the owner from the first sensor
        imported_person = import_utils.import_person(person_data=person)
        result = import_utils.import_sensor(sensors_list[1], imported_person)

        assert len(result) == 2  # expect two sensors
        assert len(self.actual) == 1
        assert self.actual[0] == self.expected_3


@pytest.mark.django_db
class TestConvertApiData:
    """tests for the convert_api_data function."""

    @property
    def actual(self):
        return [
            Device2Serializer(device).data for device in models.Device2.objects.all()
        ]

    def test_convert_api_data_anpr_sensor_only_insert_2(self, api_data_2):
        """
        provide a list of two sensors dictionaries from the anpr api and the
        the name of the parser which is the api_name. Expect to have two
        sensors created and a tuple to be returned.
        """

        result = import_utils_apis.convert_api_data(
            api_name='anpr', api_data=api_data_2
        )

        assert result == ([], 2, 0)
        assert len(self.actual) == 2

    def test_convert_api_data_anpr_sensor_three_insert_one_update(
        self, api_data, api_data_2
    ):
        """
        call the convert_api function twice with two different lists of sensors.
        The second list will contain also two sensors, one of them is the same as
        the one in the first list. the same sensor.
        Expect to have three sensors in total and one sensor being updated.
        """

        # insert the first list of sensor which should include two sensors with the ids
        # ANPR-00001-V & ANPR-00002-V.
        result_1 = import_utils_apis.convert_api_data(
            api_name='anpr', api_data=api_data
        )

        # insert the second list of sensor which should include two sensors with the ids
        # ANPR-00001-V & ANPR-00003-V. The ANPR-00001-V has different location points.
        result_2 = import_utils_apis.convert_api_data(
            api_name='anpr', api_data=api_data_2
        )

        # get the sensor with referece ANPR-00001-V because it should have been
        # updated with a new location.
        sensor_ref_00001 = next(
            (sensor for sensor in self.actual if sensor['reference'] == 'ANPR-00001-V'),
            None,
        )

        assert result_1 == ([], 2, 0)
        assert result_2 == ([], 1, 1)
        assert len(self.actual) == 3
        assert sensor_ref_00001['location']['longitude'] == 4.9999999
        assert sensor_ref_00001['location']['latitude'] == 52.999999


#     @pytest.mark.skip()
#     def test_convert_api_data_wifi_sensor_one_update_one_delete(self, api_data, api_data_2):
#         """
#         call the convert_api function twice with two different lists of sensors.
#         The second list will not contain one of the sensors of the first list.
#         Expect to have one sensor being updated and another one deleted.
#         A tuple to be returned.
#         """

#         # insert the first list of sensor which should include two sensor.
#         result_1 = import_utils_apis.convert_api_data(
#             api_name='wifi_sensor_crowd_management',
#             api_data=api_data_2
#         )

#         # insert the second list of sensor which should include one sensors.
#         result_2 = import_utils_apis.convert_api_data(
#             api_name='wifi_sensor_crowd_management',
#             api_data=api_data
#         )

#         # get the only sensor that should have been updated.
#         sensor = self.actual[0]

#         assert result_1 == ([], 2, 0)
#         assert result_2 == ([], 0, 1)
#         assert len(self.actual) == 2
#         assert sensor['location']['longitude'] == 4.901852
