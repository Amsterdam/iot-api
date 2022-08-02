import pytest
from django.conf import settings

from iot import import_utils, import_utils_apis, models
from iot.import_utils import LatLong, Location, ObservationGoal, PersonData, SensorData
from iot.serializers import DeviceSerializer


@pytest.fixture
def api_data():
    return {
        "type": "FeatureCollection",
        "name": "VIS",
        "features": [
            {
                "id": 8,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.8924874, 52.3398382]},
                "properties": {
                    "Soort": "Kentekencamera, milieuzone",
                    "Soortcode": 127,
                    "Standplaats": "Europaboulevard (s109) nabij Afrit Ringweg-Zuid (A10)",
                    "Bouwjaar": 2021,
                    "Voeding": "",
                    "Objectnummer_Amsterdam": "ANPR-00008",
                    "Objectnummer_leverancier": "",
                    "VRI_nummer": 0,
                    "Rotatie": 0,
                },
            },
            {
                "id": 88,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.86666666, 52.49494949]},
                "properties": {
                    "Soort": "No Kentekencamera, milieuzone",
                    "Soortcode": 127,
                    "Standplaats": "Europaboulevard (s109) nabij Afrit Ringweg-Zuid (A10)",
                    "Bouwjaar": 2021,
                    "Voeding": "",
                    "Objectnummer_Amsterdam": "ANPR-000088",
                    "Objectnummer_leverancier": "",
                    "VRI_nummer": 0,
                    "Rotatie": 0,
                },
            },
            {
                "id": 89,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.83883838, 52.84848484]},
                "properties": {
                    "Soort": "Kentekencamera, no milieuzone",
                    "Soortcode": 127,
                    "Standplaats": "Europaboulevard (s109) nabij Afrit Ringweg-Zuid (A10)",
                    "Bouwjaar": 2021,
                    "Voeding": "",
                    "Objectnummer_Amsterdam": "ANPR-000089",
                    "Objectnummer_leverancier": "",
                    "VRI_nummer": 0,
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
                "id": 8,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.999999, 52.3398382]},
                "properties": {
                    "Soort": "Kentekencamera, milieuzone",
                    "Soortcode": 127,
                    "Standplaats": "Europaboulevard (s109) nabij Afrit Ringweg-Zuid (A10)",
                    "Bouwjaar": 2021,
                    "Voeding": "",
                    "Objectnummer_Amsterdam": "ANPR-00008",
                    "Objectnummer_leverancier": "",
                    "VRI_nummer": 0,
                    "Rotatie": 0,
                },
            },
            {
                "id": 88,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.86666666, 52.49494949]},
                "properties": {
                    "Soort": "Kentekencamera, milieuzone",
                    "Soortcode": 127,
                    "Standplaats": "Europaboulevard (s109) nabij Afrit Ringweg-Zuid (A10)",
                    "Bouwjaar": 2021,
                    "Voeding": "",
                    "Objectnummer_Amsterdam": "ANPR-000088",
                    "Objectnummer_leverancier": "",
                    "VRI_nummer": 0,
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
        last_name="stedelijk beheer",
    )


@pytest.fixture
def sensor_data(person_data):
    return SensorData(
        owner=person_data,
        reference='ANPR-000010',
        type="Optische / camera sensor",
        location=Location(
            lat_long=LatLong(latitude=52.3398382, longitude=4.8924874),
            postcode_house_number=None,
            description='',
            regions='',
        ),
        datastream='',
        observation_goals=[
            ObservationGoal(
                observation_goal='Handhaving van verkeersbesluiten.',
                legal_ground='Verkeersbesluiten in de rol van wegbeheerder.',
                privacy_declaration="https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/milieuzones/",
            )
        ],
        themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto', 'Milieu']),
        contains_pi_data='Ja',
        active_until='01-01-2050',
        projects=[''],
    )


class TestApiParser:
    def test_parse_kentekencamera_milieuzone_expected_person_sensor_with_filter(
        self, api_data
    ):
        """
        provide a list of three dictionaries of three sensors. only one
        sensor with the soort Kentekencamera, milieuzone should be returned.
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
            last_name="stedelijk beheer",
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference='ANPR-00008',
                type="Optische / camera sensor",
                location=Location(
                    lat_long=LatLong(latitude=52.3398382, longitude=4.8924874),
                    postcode_house_number=None,
                    description='',
                    regions='',
                ),
                datastream='',
                observation_goals=[
                    ObservationGoal(
                        observation_goal='Handhaving van verkeersbesluiten.',
                        legal_ground='Verkeersbesluiten in de rol van wegbeheerder.',
                        privacy_declaration="https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/milieuzones/",
                    )
                ],
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto', 'Milieu']),
                contains_pi_data='Ja',
                active_until='01-01-2050',
                projects=[''],
            )
        ]
        sensor_list = list(
            import_utils_apis.parse_kentekencamera_milieuzone(data=api_data)
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
        'name': 'Afdeling stedelijk beheer',
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
        'location': {'latitude': 52.3398382, 'longitude': 4.8924874},
        'location_description': None,
        'observation_goals': [
            {
                'observation_goal': 'Handhaving van verkeersbesluiten.',
                'privacy_declaration': 'https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/milieuzones/',
                'legal_ground': 'Verkeersbesluiten in de rol van wegbeheerder.',
            }
        ],
        'owner': {
            'name': 'Afdeling stedelijk beheer',
            'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'regions': [],
        'themes': ['Mobiliteit: auto', 'Overig'],
        'type': 'Optische / camera sensor',
        'reference': 'ANPR-00008',
        'project_paths': [],
    }

    expected_2 = {
        'active_until': '2050-01-01',
        'contains_pi_data': True,
        'datastream': '',
        'location': {'latitude': 52.3398382, 'longitude': 4.8924874},
        'location_description': None,
        'observation_goals': [
            {
                'observation_goal': 'Handhaving van verkeersbesluiten.',
                'legal_ground': 'Verkeersbesluiten in de rol van wegbeheerder.',
                'privacy_declaration': 'https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/milieuzones/',
            }
        ],
        'owner': {
            'name': 'Afdeling stedelijk beheer',
            'email': 'Meldingsplicht.Sensoren@amsterdam.nl',
            'organisation': 'Gemeente Amsterdam',
        },
        'regions': [],
        'themes': ['Mobiliteit: auto', 'Overig'],
        'type': 'Optische / camera sensor',
        'reference': 'ANPR-000010',
        'project_paths': [],
    }

    def test_import_sensor(self, sensor_data):
        # Basic check for importing sensor data
        owner = import_utils.import_person(sensor_data.owner)
        import_utils.import_sensor(sensor_data, owner)
        assert self.actual[0] == self.expected_2

    def test_import_sensor_from_parse_kentekencamera_milieuzone_success(self, api_data):
        """
        provide a dict from the kentekencamera_milieuzone api and call
        the parser of the kentekencamera_milieuzone to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_utils_apis.parse_kentekencamera_milieuzone
        sensor_list = list(parser(api_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_utils.import_person(person_data=person)
        result = import_utils.import_sensor(sensor, imported_person)

        assert type(result[0]) == models.Device  # expect a device object to be returned
        assert self.actual[0] == self.expected_1


@pytest.mark.django_db
class TestConvertApiData:
    """tests for the convert_api_data function."""

    @property
    def actual(self):
        return [DeviceSerializer(device).data for device in models.Device.objects.all()]

    def test_convert_api_data_kentekencamera_milieuzone_only_insert_2(self, api_data_2):
        """
        provide a dict from the kenteken sensor crowd management api and the
        the name of the parser which is the api_name. Expect to have two
        sensors created and a tuple to be returned.
        """

        result = import_utils_apis.convert_api_data(
            api_name='kentekencamera_milieuzone', api_data=api_data_2
        )

        assert result == ([], 2, 0)
        assert len(self.actual) == 2

    def test_convert_api_data_kenteken_milieuzone_1_insert_1_update(
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
            api_name='kentekencamera_milieuzone', api_data=api_data
        )

        # insert the second list of sensor which should include two sensors.
        result_2 = import_utils_apis.convert_api_data(
            api_name='kentekencamera_milieuzone', api_data=api_data_2
        )

        # get the sensor with referece 2 because it should have been updated.
        sensor_ref_2 = next(
            (sensor for sensor in self.actual if sensor['reference'] == 'ANPR-00008'),
            None,
        )

        assert result_1 == ([], 1, 0)
        assert result_2 == ([], 1, 1)
        assert len(self.actual) == 2
        assert sensor_ref_2['location']['longitude'] == 4.999999

    @pytest.mark.skip("waiting for the delete function to be adjusted")
    def test_convert_api_data_kenteken_milieuzone_1_update_1_delete(
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
            api_name='kentekencamera_milieuzone', api_data=api_data_2
        )

        # insert the second list of sensor which should include one sensors.
        result_2 = import_utils_apis.convert_api_data(
            api_name='kentekencamera_milieuzone', api_data=api_data
        )

        # get the only sensor that should have been updated.
        sensor = self.actual[0]

        assert result_1 == ([], 2, 0)
        assert result_2 == ([], 1, 0)
        assert len(self.actual) == 1
        assert sensor['location']['longitude'] == 4.8924874
