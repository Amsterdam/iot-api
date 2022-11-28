import pytest
from django.conf import settings

from iot import models
from iot.dateclasses import LatLong, Location, ObservationGoal, PersonData, SensorData
from iot.importers import import_person, import_sensor, import_apis
from iot.serializers import DeviceSerializer


@pytest.fixture
def api_data():
    return {
        "type": "FeatureCollection",
        "name": "CROWDSENSOREN",
        "features": [
            {
                "id": 40,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.901853, 52.3794285]},
                "properties": {
                    "Objectnummer": "GABW-02",
                    "Soort": "WiFi sensor",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/foo/",
                },
            },
            {
                "id": 41,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.901852, 52.3794284]},
                "properties": {
                    "Objectnummer": "GABW-03",
                    "Soort": "3D sensor",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/foo/",
                },
            },
            {
                "id": 42,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.901859, 52.3794289]},
                "properties": {
                    "Objectnummer": "GABW-04",
                    "Soort": "Corona CMSA",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/foo/",
                },
            },
            {
                "id": 43,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.901858, 52.3794287]},
                "properties": {
                    "Objectnummer": "GABW-05",
                    "Soort": "Telcamera",
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
                "id": 41,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.99999, 52.3794284]},
                "properties": {
                    "Objectnummer": "GABW-03",
                    "Soort": "3D sensor",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/bar/",
                },
            },
            {
                "id": 45,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.901852, 52.3794284]},
                "properties": {
                    "Objectnummer": "GABW-06",
                    "Soort": "Telcamera",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/foo/",
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
        first_name="Afdeling",
        last_name_affix="",
        last_name="verkeersmanagment",
    )


@pytest.fixture
def sensor_data(person_data):
    """a crow management sensor fixture"""
    return SensorData(
        owner=person_data,
        reference='GABW-06',
        type="Optische / camera sensor",
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
    )


class TestApiParser:
    def test_parse_sensor_crowd_management_expected_persondata_sensor(self, api_data):
        """
        provide a dict object with a list of sensoren from the sensor crowd management api.
        The sensors list will contain two sensor with different Soort attribute. Expect
        to get back three sensors only and the person is the expected one.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="LVMA@amsterdam.nl",
            telephone="14020",
            website="https://www.amsterdam.nl/",
            first_name="Afdeling",
            last_name_affix="",
            last_name="verkeersmanagment",
        )
        # expected_value is a sensors
        expected_sensors = [
            SensorData(
                owner=expected_owner,
                reference='GABW-03',
                type="Optische / camera sensor",
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
            ),
            SensorData(
                owner=expected_owner,
                reference='GABW-04',
                type="Optische / camera sensor",
                location=Location(
                    lat_long=LatLong(latitude=52.3794289, longitude=4.901859),
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
            ),
            SensorData(
                owner=expected_owner,
                reference='GABW-05',
                type="Optische / camera sensor",
                location=Location(
                    lat_long=LatLong(latitude=52.3794287, longitude=4.901858),
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
            ),
        ]
        sensor_list = list(
            import_apis.parse_sensor_crowd_management(data=api_data)
        )

        assert len(sensor_list) == 3

        owner = sensor_list[0].owner

        assert expected_sensors == sensor_list
        assert owner == expected_owner


@pytest.mark.django_db
class TestConvertApiData:
    """tests for the convert_api_data function."""

    @property
    def actual(self):
        return [DeviceSerializer(device).data for device in models.Device.objects.all()]

    def test_convert_api_data_sensor_only_insert_2(self, api_data_2):
        """
        provide a dict from the  sensor crowd management api and the
        the name of the parser which is the api_name. Expect to have two
        sensors created and a tuple to be returned.
        """

        result = import_apis.convert_api_data(
            api_name='sensor_crowd_management', api_data=api_data_2
        )

        assert result == ([], 2, 0)
        assert len(self.actual) == 2

    def test_convert_api_data_sensor_3_inserts_1_update(self, api_data, api_data_2):
        """
        call the convert_api function twice with two different lists of sensors.
        The second list will contain the same sensor as in the first list.
        Expect to have one sensor being updated and another 3 inserted.
        A tuple to be returned.
        """

        # insert the first list of sensor which should include only one sensor.
        result_1 = import_apis.convert_api_data(
            api_name='sensor_crowd_management', api_data=api_data
        )

        # insert the second list of sensor which should include two sensors.
        result_2 = import_apis.convert_api_data(
            api_name='sensor_crowd_management', api_data=api_data_2
        )

        # get the sensor with referece 41 because it should have been updated.
        sensor_ref_2 = next(
            (sensor for sensor in self.actual if sensor['reference'] == 'GABW-03'), None
        )

        assert result_1 == ([], 3, 0)
        assert result_2 == ([], 1, 1)
        assert len(self.actual) == 4
        assert sensor_ref_2['location']['longitude'] == 4.99999

    @pytest.mark.skip()
    def test_convert_api_data_sensor_one_update_one_delete(self, api_data, api_data_2):
        """
        call the convert_api function twice with two different lists of sensors.
        The second list will not contain one of the sensors of the first list.
        Expect to have one sensor being updated, two inserted and another one
        deleted. A tuple to be returned.
        """

        # insert the first list of sensor which should include two sensor.
        result_1 = import_apis.convert_api_data(
            api_name='sensor_crowd_management', api_data=api_data_2
        )

        # insert the second list of sensor which should include one sensors.
        result_2 = import_apis.convert_api_data(
            api_name='sensor_crowd_management', api_data=api_data
        )

        # get the only sensor that should have been updated.
        sensor = self.actual[0]

        assert result_1 == (
            [],
            2,
            0,
        )  # confirm the first insert only inserted two records
        assert result_2 == ([], 2, 1)  # confirm thar there is an update only
        assert len(self.actual) == 3
        assert sensor['location']['longitude'] == 4.901852
