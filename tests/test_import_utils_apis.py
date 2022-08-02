import pytest
from django.conf import settings

from iot import import_utils, import_utils_apis, models
from iot.import_utils import LatLong, ObservationGoal, PersonData, SensorData
from iot.serializers import DeviceSerializer


@pytest.fixture
def sensor_data_delete():
    return {
        "type": "FeatureCollection",
        "name": "CROWDSENSOREN",
        "features": [
            {
                "id": 100,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.901853, 52.3794285]},
                "properties": {
                    "Objectnummer": "GABW-03",
                    "Soort": "WiFi sensor",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/foo/",
                },
            },
            {
                "id": 101,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.9018522, 52.3794284]},
                "properties": {
                    "Objectnummer": "GABW-03",
                    "Soort": "WiFi sensor",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/foo/",
                },
            },
            {
                "id": 102,
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.9018523, 52.3794285]},
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


@pytest.mark.django_db
class TestDeleteNotFoundSensor:
    """
    tests the delete sensor function. make sure it only deletes sensors that belong to the same
    source and do not exist.
    """

    @property
    def actual(self):
        return [DeviceSerializer(device).data for device in models.Device.objects.all()]

    @pytest.mark.skip()
    def test_delete_one_sensor_from_three_sensors(self, sensor_data_delete):
        """
        provide three sensors to be created for the wifi sensor crowd management.
        after that provide only two same sensors to the delete_sensor function from the
        same source. expect to have only two sensors remaining and one deleted.
        """
        parser = import_utils_apis.parse_wifi_sensor_crowd_management
        sensor_list = list(parser(sensor_data_delete))
        for sensor in sensor_list:
            person = sensor.owner
            imported_person = import_utils.import_person(person_data=person)
            import_utils.import_sensor(sensor, imported_person)

        assert len(self.actual) == 3

        # list of sensor objects for the delete function
        person = PersonData(
            organisation="Gemeente Amsterdam",
            email="LVMA@amsterdam.nl",
            telephone="14020",
            website="https://www.amsterdam.nl/",
            first_name="verkeers",
            last_name_affix="",
            last_name="onderzoek",
        )

        sensor1 = SensorData(
            owner=person,
            reference='wifi_sensor_crowd_management_100',
            type="Aanwezigheid of nabijheidsensor",
            location=LatLong(latitude=4.901852, longitude=52.3794284),
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
        )

        sensor2 = SensorData(
            owner=person,
            reference='wifi_sensor_crowd_management_101',
            type="Aanwezigheid of nabijheidsensor",
            location=LatLong(latitude=4.901853, longitude=52.3794284),
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
        )

        sensors_list = [sensor1, sensor2]
        import_utils_apis.delete_not_found_sensors(
            sensors=sensors_list, source='wifi_sensor_crowd_management'
        )

        assert len(self.actual) == 2
        assert self.actual[0]['reference'] == 'wifi_sensor_crowd_management_100'
        assert self.actual[1]['reference'] == 'wifi_sensor_crowd_management_101'
        assert self.actual[0]['owner']['email'] == 'LVMA@amsterdam.nl'

    @pytest.mark.skip()
    def test_delete_no_sensor_different_source(self, sensor_data_delete):
        """provide three sensors to be created for the wifi sensor crowd management. after that provide
        only two same sensors to the delete_sensor function from the a different source.
        expect to have no sensor deleted from the wifi_sensor_crowd_management."""
        parser = import_utils_apis.parse_wifi_sensor_crowd_management
        sensor_list = list(parser(sensor_data_delete))
        for sensor in sensor_list:
            person = sensor.owner
            imported_person = import_utils.import_person(person_data=person)
            import_utils.import_sensor(sensor, imported_person)

        assert len(self.actual) == 3

        person = PersonData(
            organisation="Gemeente Amsterdam",
            email="verkeersonderzoek@amsterdam.nl",
            telephone="14020",
            website="https://www.amsterdam.nl/",
            first_name="verkeers",
            last_name_affix="",
            last_name="onderzoek",
        )
        # list of sensor objects for the delete function
        sensor1 = SensorData(
            owner=person,
            reference='sensor_crowd_management_100',
            type="Aanwezigheid of nabijheidsensor",
            location=LatLong(latitude=4.901852, longitude=52.3794284),
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
        )

        sensor2 = SensorData(
            owner=person,
            reference='sensor_crowd_management_101',
            type="Aanwezigheid of nabijheidsensor",
            location=LatLong(latitude=4.901853, longitude=52.3794284),
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
        )

        sensors_list = [sensor1, sensor2]
        result = import_utils_apis.delete_not_found_sensors(
            sensors=sensors_list, source='sensor_crowd_management'
        )

        assert result == (0, {})
        assert len(self.actual) == 3
        assert self.actual[0]['reference'] == 'wifi_sensor_crowd_management_100'
        assert self.actual[1]['reference'] == 'wifi_sensor_crowd_management_101'
        assert self.actual[2]['reference'] == 'wifi_sensor_crowd_management_102'
        assert self.actual[0]['owner']['email'] == 'LVMA@amsterdam.nl'


class TestUrlAdjusterForLegalDeclarations:
    """
    tests for the adjust_url function that adds the https:// to the privacy_declaration
    url.
    """

    def test_adjust_url_with_https(self):
        """provide a url that starts with https://. expect the same url will be returned."""

        privacy_declaration_url = "https://www.amsterdam.nl/foo/"
        returned_url = import_utils_apis.adjust_url(privacy_declaration_url)

        assert returned_url == privacy_declaration_url

    def test_adjust_url_without_https(self):
        """provide a url that doesn't starts with https://. expect the same
        url will be returned with https://."""

        privacy_declaration_url = "www.amsterdam.nl/foo/"
        expected_url = "https://www.amsterdam.nl/foo/"
        returned_url = import_utils_apis.adjust_url(privacy_declaration_url)

        assert returned_url == expected_url

    def test_adjust_url_with_space(self):
        """provide a url that contains space at the end. expect the same
        url will be returned without space."""

        privacy_declaration_url = "https://www.amsterdam.nl/foo/ "
        expected_url = "https://www.amsterdam.nl/foo/"
        returned_url = import_utils_apis.adjust_url(privacy_declaration_url)

        assert returned_url == expected_url
