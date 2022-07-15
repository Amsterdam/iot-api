import pytest
from django.conf import settings

from iot import import_utils, import_utils_apis, models
from iot.import_utils import LatLong, Location, ObservationGoal, PersonData, SensorData
from iot.serializers import DeviceSerializer


@pytest.fixture
def api_data():
    return {
        "type": "FeatureCollection",
        "name": "PRIVACY_BRUGSLUIS",
        "features": [
            {
                "id": 1,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.793372, 52.343909]},
                "properties": {
                    "Naam": "Akersluis",
                    "BrugSluisNummer": "SLU0101",
                    "Actief_JN": "Ja",
                    "Eigenaar": "VOR",
                    "Privacyverklaring": "https://www.amsterdam.nl/privacy/privacylink/",
                },
            }
        ],
    }


@pytest.fixture
def api_data_2():  # a second list of api data sensors
    return {
        "type": "FeatureCollection",
        "name": "PRIVACY_BRUGSLUIS",
        "features": [
            {
                "id": 1,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.999999, 52.343909]},
                "properties": {
                    "Naam": "Akersluis",
                    "BrugSluisNummer": "SLU0101",
                    "Actief_JN": "Ja",
                    "Eigenaar": "VOR",
                    "Privacyverklaring": "https://www.amsterdam.nl/privacy/privacylink/",
                },
            },
            {
                "id": 12,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.2344333, 52.343909]},
                "properties": {
                    "Naam": "Akersluis",
                    "BrugSluisNummer": "SLU0112",
                    "Actief_JN": "Ja",
                    "Eigenaar": "VOR",
                    "Privacyverklaring": "https://www.amsterdam.nl/privacy/privacylink/",
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
        last_name="stedelijkbeheer",
    )


@pytest.fixture
def sensor_data(person_data):
    return SensorData(
        owner=person_data,
        reference='SLU0102',
        type="Optische / camera sensor",
        location=Location(
            lat_long=LatLong(latitude=52.343909, longitude=4.793372),
            postcode_house_number=None,
            description='',
            regions='',
        ),
        datastream='',
        observation_goals=[
            ObservationGoal(
                observation_goal='Het bedienen van sluisen en bruggen.',
                legal_ground='Sluisbeheerder in het kader van de woningwet 1991',
                privacy_declaration="https://www.amsterdam.nl/privacy/privacylink/",
            )
        ],
        themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
        contains_pi_data='Ja',
        active_until='01-01-2050',
        projects=[''],
    )


class TestApiParser:
    def test_parse_camera_brug_en_sluisbediening_expected_sensor(self, api_data):
        """
        provide a list of dict object from the wifi sonso camera brug en
        sluisbediening api. The sensors list will contain one sensor.
        Expect to get back the only sensor with the expected person.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="Meldingsplicht.Sensoren@amsterdam.nl",
            telephone="14020",
            website="https://www.amsterdam.nl/",
            first_name="Afdeling",
            last_name_affix="",
            last_name="stedelijkbeheer",
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference='SLU0101',
                type="Optische / camera sensor",
                location=Location(
                    lat_long=LatLong(latitude=52.343909, longitude=4.793372),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                datastream='',
                observation_goals=[
                    ObservationGoal(
                        observation_goal='Het bedienen van sluisen en bruggen.',
                        legal_ground='Sluisbeheerder in het kader van de woningwet 1991',
                        privacy_declaration="https://www.amsterdam.nl/privacy/privacylink/",
                    )
                ],
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Ja',
                active_until='01-01-2050',
                projects=[''],
            )
        ]
        sensor_list = list(
            import_utils_apis.parse_camera_brug_en_sluisbediening(data=api_data)
        )
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
        return list(models.Person.objects.values(*fields).order_by('id').all())

    expected = {
        'organisation': 'Gemeente Amsterdam',
        'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
        'telephone': '14020',
        'website': 'https://www.amsterdam.nl/',
        'name': 'Afdeling stedelijkbeheer',
    }

    def test_import_person(self, person_data):
        import_utils.import_person(person_data)
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
        'location': {'latitude': 52.343909, 'longitude': 4.793372},
        'location_description': None,
        'observation_goals': [
            {
                'observation_goal': 'Het bedienen van sluisen en bruggen.',
                'legal_ground': 'Sluisbeheerder in het kader van de woningwet 1991',
                'privacy_declaration': 'https://www.amsterdam.nl/privacy/privacylink/',
            }
        ],
        'owner': {
            'name': 'Afdeling stedelijkbeheer',
            'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Optische / camera sensor',
        'reference': 'SLU0101',
        'project_paths': [],
    }

    expected_2 = {
        'active_until': '2050-01-01',
        'contains_pi_data': True,
        'datastream': '',
        'location': {'latitude': 52.343909, 'longitude': 4.793372},
        'location_description': None,
        'observation_goals': [
            {
                'observation_goal': 'Het bedienen van sluisen en bruggen.',
                'legal_ground': 'Sluisbeheerder in het kader van de woningwet 1991',
                'privacy_declaration': 'https://www.amsterdam.nl/privacy/privacylink/',
            }
        ],
        'owner': {
            'name': 'Afdeling stedelijkbeheer',
            'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'regions': [],
        'themes': ['Mobiliteit: auto'],
        'type': 'Optische / camera sensor',
        'reference': 'SLU0102',
        'project_paths': [],
    }

    def test_import_sensor(self, sensor_data):
        # Basic check for importing sensor data
        owner = import_utils.import_person(sensor_data.owner)
        import_utils.import_sensor(sensor_data, owner)
        assert self.actual[0] == self.expected_2

    def test_import_sensor_from_camera_brug_en_sluisbediening(self, api_data):
        """
        provide a dict from the camera_brug_en_sluisbediening api and call
        the parser of the camera_brug_en_sluisbediening to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_utils_apis.parse_camera_brug_en_sluisbediening
        sensor_list = list(parser(api_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_utils.import_person(person_data=person)
        result = import_utils.import_sensor(sensor, imported_person)

        assert type(result[0]) == models.Device  # expet a device2 object to be returned
        assert self.actual[0] == self.expected_1


@pytest.mark.django_db
class TestConvertApiData:
    """tests for the convert_api_data function."""

    @property
    def actual(self):
        return [DeviceSerializer(device).data for device in models.Device.objects.all()]

    def test_convert_api_data_brug_en_sluis_only_insert_2(self, api_data_2):
        """
        provide a dict from the wifi sensor crowd management api and the
        the name of the parser which is the api_name. Expect to have two
        sensors created and a tuple to be returned.
        """

        result = import_utils_apis.convert_api_data(
            api_name='camera_brug_en_sluisbediening', api_data=api_data_2
        )

        assert result == ([], 2, 0)
        assert len(self.actual) == 2

    def test_convert_api_data_brug_en_sluis_one_insert_one_update(
        self, api_data, api_data_2
    ):
        """
        call the convert_api function twice with two different lists of sensors.
        The second list will contain the same sensor as in the first list.
        Expect to have one sensor being updated and another one inserted.
        A tuple to be returned.
        """

        # insert the first list of sensor which should include only one sensor.
        result_1 = import_utils_apis.convert_api_data(
            api_name='camera_brug_en_sluisbediening', api_data=api_data
        )

        # insert the second list of sensor which should include two sensors.
        result_2 = import_utils_apis.convert_api_data(
            api_name='camera_brug_en_sluisbediening', api_data=api_data_2
        )

        # get the sensor with referece 2 because it should have been updated.
        sensor_ref_2 = next(
            (sensor for sensor in self.actual if sensor['reference'] == 'SLU0101'), None
        )

        assert result_1 == ([], 1, 0)
        assert result_2 == ([], 1, 1)
        assert len(self.actual) == 2
        assert sensor_ref_2['location']['latitude'] == 52.343909

    @pytest.mark.skip("waiting for the delete function to be adjusted")
    def test_convert_api_data_brug_en_sluis_one_update_one_delete(
        self, api_data, api_data_2
    ):
        """
        call the convert_api function twice with two different lists of sensors.
        The second list will not contain one of the sensors of the first list.
        Expect to have one sensor being updated and another one deleted.
        A tuple to be returned.
        """

        # insert the first list of sensor which should include two sensor.
        result_1 = import_utils_apis.convert_api_data(
            api_name='camera_brug_en_sluisbediening', api_data=api_data_2
        )

        # insert the second list of sensor which should include one sensors.
        result_2 = import_utils_apis.convert_api_data(
            api_name='camera_brug_en_sluisbediening', api_data=api_data
        )

        # get the only sensor that should have been updated.
        sensor = self.actual[0]

        assert result_1 == ([], 2, 0)
        assert result_2 == ([], 0, 1)
        assert len(self.actual) == 1
        assert sensor['location']['latitude'] == 52.343909
