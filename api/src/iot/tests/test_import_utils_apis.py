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
def wscm_data_delete():  # wifi_sensor_crowd_management
    return {
        "type": "FeatureCollection",
        "name": "CROWDSENSOREN",
        "features": [
            {
                "id": 100,
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
                    "Soort": "WiFi sensor",
                    "Voeding": "Vaste spanning",
                    "Rotatie": 0,
                    "Actief": "Ja",
                    "Privacyverklaring": "https://www.amsterdam.nl/foo/"
                }
            },
            {
                "id": 101,
                "type": "Feature",
                "geometry":
                {
                    "type": "Point",
                    "coordinates": [
                        4.9018522,
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
            {
                "id": 102,
                "type": "Feature",
                "geometry":
                {
                    "type": "Point",
                    "coordinates": [
                        4.9018523,
                        52.3794285
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
def cbes_data():  # camera_brug_en_sluisbediening
    return {
        "type": "FeatureCollection",
        "name": "PRIVACY_BRUGSLUIS",
        "features": [
            {
                "id": 1,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.793372,
                        52.343909
                    ]
                },
                "properties": {
                    "Naam": "Akersluis",
                    "BrugSluisNummer": "SLU0102",
                    "Actief_JN": "Ja",
                    "Eigenaar": "VOR",
                    "Privacyverklaring": "https://www.amsterdam.nl/privacy/privacylink/"
                }
            }
        ]
    }


@pytest.fixture
def cctvcv_data():  # cctv_camera_verkeersmanagement
    return {
        "type": "FeatureCollection",
        "name": "VIS",
        "features": [
            {
                "id": 16,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.895861,
                        52.381541
                    ]
                },
                "properties": {
                    "Soort": "Ignore TV Camera",
                    "Soortcode": 111,
                    "Standplaats": "De Ruyterkade - Havengebouw",
                    "Bouwjaar": 2015,
                    "Voeding": "Uit havengebouw",
                    "Objectnummer_Amsterdam": "TV-117-054",
                    "Objectnummer_leverancier": "TAC64",
                    "VRI_nummer": 117,
                    "Rotatie": 0
                }
            },
            {
                "id": 5,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.895862,
                        52.381543
                    ]
                },
                "properties": {
                    "Soort": "TV Camera",
                    "Soortcode": 111,
                    "Standplaats": "De Ruyterkade - Havengebouw",
                    "Bouwjaar": 2015,
                    "Voeding": "Uit havengebouw",
                    "Objectnummer_Amsterdam": "TV-117-054",
                    "Objectnummer_leverancier": "TAC64",
                    "VRI_nummer": 117,
                    "Rotatie": 0
                }
            },
            {
                "id": 15,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.8958601,
                        52.3815401
                    ]
                },
                "properties": {
                    "Soort": "No TV Camera",
                    "Soortcode": 111,
                    "Standplaats": "De Ruyterkade - Havengebouw",
                    "Bouwjaar": 2015,
                    "Voeding": "Uit havengebouw",
                    "Objectnummer_Amsterdam": "TV-117-054",
                    "Objectnummer_leverancier": "TAC64",
                    "VRI_nummer": 117,
                    "Rotatie": 0
                }
            }
        ]
    }


@pytest.fixture
def kcr_data():  # kentekencamera_reistijd
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
                    "Objectnummer_Amsterdam": "ANPR-03040",
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
                    "Objectnummer_Amsterdam": "ANPR-03040",
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
                    "Objectnummer_Amsterdam": "ANPR-03040",
                    "Objectnummer_leverancier": "",
                    "VRI_nummer": 101,
                    "Rotatie": 0
                }
            }
        ]
    }


@pytest.fixture
def km_data():  # kentekencamera_milieuzone
    return {
        "type": "FeatureCollection",
        "name": "VIS",
        "features": [
            {
                "id": 8,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.8924874,
                        52.3398382
                    ]
                },
                "properties": {
                    "Soort": "Kentekencamera, milieuzone",
                    "Soortcode": 127,
                    "Standplaats": "Europaboulevard (s109) nabij Afrit Ringweg-Zuid (A10)",
                    "Bouwjaar": 2021,
                    "Voeding": "",
                    "Objectnummer_Amsterdam": "ANPR-01061",
                    "Objectnummer_leverancier": "",
                    "VRI_nummer": 0,
                    "Rotatie": 0
                }
            },
            {
                "id": 88,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.86666666,
                        52.49494949
                    ]
                },
                "properties": {
                    "Soort": "No Kentekencamera, milieuzone",
                    "Soortcode": 127,
                    "Standplaats": "Europaboulevard (s109) nabij Afrit Ringweg-Zuid (A10)",
                    "Bouwjaar": 2021,
                    "Voeding": "",
                    "Objectnummer_Amsterdam": "ANPR-01061",
                    "Objectnummer_leverancier": "",
                    "VRI_nummer": 0,
                    "Rotatie": 0
                }
            },
            {
                "id": 89,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.83883838,
                        52.84848484
                    ]
                },
                "properties": {
                    "Soort": "Kentekencamera, no milieuzone",
                    "Soortcode": 127,
                    "Standplaats": "Europaboulevard (s109) nabij Afrit Ringweg-Zuid (A10)",
                    "Bouwjaar": 2021,
                    "Voeding": "",
                    "Objectnummer_Amsterdam": "ANPR-01061",
                    "Objectnummer_leverancier": "",
                    "VRI_nummer": 0,
                    "Rotatie": 0
                }
            }
        ]
    }


@pytest.fixture
def am_data():  # ais_masten
    return {
        "type": "FeatureCollection",
        "name": "PRIVACY_AISMASTEN",
        "features": [
            {
                "id": 9,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.899393,
                        52.4001061
                    ]
                },
                "properties":
                {
                    "Locatienaam": "Floating office",
                    "Privacyverklaring": "https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/vaarwegbeheer/"
                }
            }
        ]
    }


@pytest.fixture
def vomc_data():  # verkeersonderzoek_met_cameras
    return {
        "type": "FeatureCollection",
        "name": "PRIVACY_OVERIG",
        "features": [
            {
                "id": 10,
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.9021014,
                        52.3689078
                    ]
                },
                "properties": {
                    "Soort": "Touringcaronderzoek",
                    "Omschrijving": "Verkeersonderzoek",
                    "Privacyverklaring": "www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/artikel-3/"
                }
            }
        ]
    }


@pytest.fixture
def bfa_data():  # beweegbare_fysieke_afsluiting
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


class TestApiParser:

    def test_parse_wifi_sensor_crowd_management_expected_persondata_sensor(self, wscm_data):
        """
        provide a list of dict object from the wifi sonso crowd management api.
        The sensors list will contain two sensor with different Soort attribute. Expect
        to get back one sensor only and the person is the expected one.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="LVMA@amsterdam.nl",
            telephone="06123456",
            website="https://acc.sensorenregister.amsterdam.nl",
            first_name="verkeers",
            last_name_affix="v",
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

    def test_parse_camera_brug_en_sluisbediening_expected_sensor(self, cbes_data):
        """
        provide a list of dict object from the wifi sonso camera brug en
        sluisbediening api. The sensors list will contain one sensor.
        Expect to get back the only sensor with the expected person.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="stedelijkbeheer@amsterdam.nl",
            telephone="06123456",
            website="https://acc.sensorenregister.amsterdam.nl",
            first_name="stedelijk",
            last_name_affix="v",
            last_name="beheer"
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference=1,
                type="Feature",
                location=LatLong(latitude=4.793372, longitude=52.343909),
                datastream='',
                observation_goal='Het bedienen van sluisen en bruggen.',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Ja',
                legal_ground='Sluisbeheerder in het kader van de woningwet 1991',
                privacy_declaration="https://www.amsterdam.nl/privacy/privacylink/",
                active_until='01-01-2050'
            )
        ]
        sensor_list = list(import_utils_apis.parse_camera_brug_en_sluisbediening(data=cbes_data))
        sensor = sensor_list[0]  # expect the first and only element
        owner = sensor.owner

        assert len(sensor_list) == 1
        assert sensor == expected[0]
        assert owner == expected_owner

    def test_parse_cctv_camera_verkeersmanagement_one_person_sensor_with_filter(self, cctvcv_data):
        """
        provide a list of three dictionaries of three sensors. only one
        sensor with the soort TV Camera should be returned.
        The sensor and the owner should match the expected data.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="verkeersmanagement@amsterdam.nl",
            telephone="06123456",
            website="https://acc.sensorenregister.amsterdam.nl",
            first_name="camera",
            last_name_affix="en",
            last_name="verkeersmanagement"
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference=5,
                type="Feature",
                location=LatLong(latitude=4.895862, longitude=52.381543),
                datastream='',
                observation_goal='Waarnemen van het verkeer.',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagment in de rol van wegbeheerder.',
                privacy_declaration="https://www.amsterdam.nl/privacy/\
specifieke/privacyverklaring-parkeren-verkeer-bouw/verkeersmanagement",
                active_until='01-01-2050'
            )
        ]
        sensor_list = list(import_utils_apis.parse_cctv_camera_verkeersmanagement(data=cctvcv_data))
        sensor_data = sensor_list[0]
        person_data = sensor_data.owner

        assert len(sensor_list) == 1
        assert sensor_data == expected[0]
        assert person_data == expected_owner

    def test_parse_kentekencamera_reistijd_expected_person_sensor_with_filter(self, kcr_data):
        """
        provide a list of three dictionaries of three sensors. only one
        sensor with the soort Kentekencamera, reistijd (MoCo) should be returned.
        The sensor and the owner should match the expected data.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="kentekencamera@amsterdam.nl",
            telephone="06123456",
            website="https://acc.sensorenregister.amsterdam.nl",
            first_name="kentekencamera",
            last_name_affix="en",
            last_name="reistijd"
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference=7,
                type="Feature",
                location=LatLong(latitude=4.88154200, longitude=52.3851890),
                datastream='',
                observation_goal='Het tellen van voertuigen en meten van doorstroming.',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
                privacy_declaration="https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaring-parkeren-verkeer-bouw/reistijden-meetsysteem-privacy/",
                active_until='01-01-2050'
            )
        ]
        sensor_list = list(import_utils_apis.parse_kentekencamera_reistijd(data=kcr_data))
        sensor_data = sensor_list[0]
        person_data = sensor_data.owner

        assert len(sensor_list) == 1
        assert sensor_data == expected[0]
        assert person_data == expected_owner

    def test_parse_kentekencamera_milieuzone_expected_person_sensor_with_filter(self, km_data):
        """
        provide a list of three dictionaries of three sensors. only one
        sensor with the soort Kentekencamera, milieuzone should be returned.
        The sensor and the owner should match the expected data.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="kentekencameramilieuzone@amsterdam.nl",
            telephone="06123456",
            website="https://acc.sensorenregister.amsterdam.nl",
            first_name="kentekencamera",
            last_name_affix="en",
            last_name="milieuzone"
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference=8,
                type="Feature",
                location=LatLong(latitude=4.8924874, longitude=52.3398382),
                datastream='',
                observation_goal='Handhaving van verkeersbesluiten.',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto', 'Milieu']),
                contains_pi_data='Ja',
                legal_ground='Verkeersbesluiten in de rol van wegbeheerder.',
                privacy_declaration="https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/milieuzones/",
                active_until='01-01-2050'
            )
        ]
        sensor_list = list(import_utils_apis.parse_kkentekencamera_milieuzone(data=km_data))
        sensor_data = sensor_list[0]
        person_data = sensor_data.owner

        assert len(sensor_list) == 1
        assert sensor_data == expected[0]
        assert person_data == expected_owner

    def test_parse_ais_masten_expected_person_sensor_1_sensor(self, am_data):
        """
        provide a list of 1 dictionary object and expect back a sensordata
        and persondata that matches the expected data.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="programmavaren@amsterdam.nl",
            telephone="06123456",
            website="https://acc.sensorenregister.amsterdam.nl",
            first_name="ais",
            last_name_affix="en",
            last_name="masten"
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference=9,
                type="Feature",
                location=LatLong(latitude=4.899393, longitude=52.4001061),
                datastream='',
                observation_goal='Vaarweg management',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Ja',
                legal_ground='In de rol van vaarwegbeheerder op basis van de binnenvaartwet.',
                privacy_declaration="https://www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/vaarwegbeheer/",
                active_until='01-01-2050'
            )
        ]
        sensor_list = list(import_utils_apis.parse_ais_masten(data=am_data))
        sensor_data = sensor_list[0]
        person_data = sensor_data.owner

        assert sensor_data == expected[0]
        assert person_data == expected_owner

    def test_parse_verkeersonderzoek_met_cameras_expected_person_sensor(self, vomc_data):
        """
        provide a list of 1 dictionary object and expect back a sensordata
        and persondata that matches the expected data.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="verkeersonderzoek@amsterdam.nl",
            telephone="06123456",
            website="https://acc.sensorenregister.amsterdam.nl",
            first_name="verkeers",
            last_name_affix="en",
            last_name="onderzoek"
        )
        # expected_value is a sensors
        expected = [
            SensorData(
                owner=expected_owner,
                reference=10,
                type="Feature",
                location=LatLong(latitude=4.9021014, longitude=52.3689078),
                datastream='',
                observation_goal='Tellen van voertuigen.',
                themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
                contains_pi_data='Ja',
                legal_ground='Verkeersmanagement in de rol van wegbeheerder.',
                privacy_declaration="www.amsterdam.nl/privacy/specifieke/\
privacyverklaringen-b/artikel-3/",
                active_until='01-01-2050'
            )
        ]
        sensor_list = list(import_utils_apis.parse_verkeersonderzoek_met_cameras(
            data=vomc_data
        ))
        sensor_data = sensor_list[0]
        person_data = sensor_data.owner

        assert sensor_data == expected[0]
        assert person_data == expected_owner

    def test_parse_beweegbare_fysieke_afsluiting_expected_person_sensor(self, bfa_data):
        """
        provide a list of 1 dictionary object and expect back a sensordata
        and persondata that matches the expected data.
        """
        # expected owner
        expected_owner = PersonData(
            organisation="Gemeente Amsterdam",
            email="beweegbarefysiek@amsterdam.nl",
            telephone="06123456",
            website="https://acc.sensorenregister.amsterdam.nl",
            first_name="beweegbare",
            last_name_affix="en",
            last_name="afsluiting"
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
                privacy_declaration="N/A",
                active_until='01-01-2050'
            )
        ]
        sensor_list = list(import_utils_apis.parse_beweegbare_fysieke_afsluiting(
            data=bfa_data
        ))
        sensor_data = sensor_list[0]
        person_data = sensor_data.owner

        assert sensor_data == expected[0]
        assert person_data == expected_owner


@pytest.fixture
def person_data():
    return PersonData(
        organisation="Gemeente Amsterdam",
        email="LVMA@amsterdam.nl",
        telephone="06123456",
        website="https://acc.sensorenregister.amsterdam.nl",
        first_name="verkeers",
        last_name_affix="v",
        last_name="onderzoek"
    )


@pytest.mark.django_db
class TestImportPerson:

    @property
    def actual(self):
        fields = 'organisation', 'email', 'telephone', 'website', 'name'
        return list(models.Person2.objects.values(*fields).order_by('id').all())

    expected = {
        'organisation': 'Gemeente Amsterdam',
        'email': 'LVMA@amsterdam.nl',
        'telephone': '06123456',
        'website': 'https://acc.sensorenregister.amsterdam.nl',
        'name': 'verkeers v onderzoek',
    }

    def test_import_person(self, person_data):
        import_utils.import_person(person_data)
        assert self.actual == [self.expected]


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


@pytest.mark.django_db
class TestImportSensor:

    @property
    def actual(self):
        return [
            Device2Serializer(device).data
            for device in models.Device2.objects.all()
        ]

    expected = {
        'active_until': '2050-01-01',
        'contains_pi_data': True,
        'datastream': '',
        'legal_ground': 'Verkeersmanagment in de rol van wegbeheerder.',
        'location': {'latitude': 4.901852, 'longitude': 52.3794284},
        'location_description': None,
        'observation_goal': 'Tellen van mensen.',
        'owner': {
            'name': 'verkeers v onderzoek',
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
        assert self.actual[0] == self.expected

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
        created_sensor = result[0]
        assert str(created_sensor.type) == 'Feature'
        assert int(created_sensor.reference) == 2

    def test_import_sensor_from_camera_brug_en_sluisbediening(self, cbes_data):
        """
        provide a dict from the camera_brug_en_sluisbediening api and call
        the parser of the camera_brug_en_sluisbediening to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_utils_apis.parse_camera_brug_en_sluisbediening
        sensor_list = list(parser(cbes_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_utils.import_person(person_data=person)
        result = import_utils.import_sensor(sensor, imported_person)
        created_sensor = result[0]
        assert str(created_sensor.type) == 'Feature'
        assert int(created_sensor.reference) == 1

    def test_import_sensor_from_parse_cctv_camera_verkeersmanagement_success(self, cctvcv_data):
        """
        provide a dict from the cctv_camera_verkeersmanagement api and call
        the parser of the cctv_camera_verkeersmanagement to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_utils_apis.parse_cctv_camera_verkeersmanagement
        sensor_list = list(parser(cctvcv_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_utils.import_person(person_data=person)
        result = import_utils.import_sensor(sensor, imported_person)
        created_sensor = result[0]
        assert str(created_sensor.type) == 'Feature'
        assert int(created_sensor.reference) == 5

    def test_import_sensor_from_parse_kentekencamera_reistijd_success(self, kcr_data):
        """
        provide a dict from the kentekencamera_reistijd api and call
        the parser of the kentekencamera_reistijd to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_utils_apis.parse_kentekencamera_reistijd
        sensor_list = list(parser(kcr_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_utils.import_person(person_data=person)
        result = import_utils.import_sensor(sensor, imported_person)
        created_sensor = result[0]
        assert str(created_sensor.type) == 'Feature'
        assert int(created_sensor.reference) == 7

    def test_import_sensor_from_parse_kentekencamera_milieuzone_success(self, km_data):
        """
        provide a dict from the kentekencamera_milieuzone api and call
        the parser of the kentekencamera_milieuzone to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_utils_apis.parse_kkentekencamera_milieuzone
        sensor_list = list(parser(km_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_utils.import_person(person_data=person)
        result = import_utils.import_sensor(sensor, imported_person)
        created_sensor = result[0]
        assert str(created_sensor.type) == 'Feature'
        assert int(created_sensor.reference) == 8

    def test_import_sensor_from_parse_ais_masten_success(self, am_data):
        """
        provide a dict from the ais_masten api and call
        the parser of the ais_masten to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_utils_apis.parse_ais_masten
        sensor_list = list(parser(am_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_utils.import_person(person_data=person)
        result = import_utils.import_sensor(sensor, imported_person)
        created_sensor = result[0]
        assert str(created_sensor.type) == 'Feature'
        assert int(created_sensor.reference) == 9

    def test_import_sensor_from_parse_verkeersonderzoek_met_cameras_success(self, vomc_data):
        """
        provide a dict from the verkeersonderzoek_met_cameras api and call
        the parser of the verkeersonderzoek_met_cameras to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_utils_apis.parse_verkeersonderzoek_met_cameras
        sensor_list = list(parser(vomc_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_utils.import_person(person_data=person)
        result = import_utils.import_sensor(sensor, imported_person)
        created_sensor = result[0]
        assert str(created_sensor.type) == 'Feature'
        assert int(created_sensor.reference) == 10

    def test_import_sensor_from_parse_beweegbare_fysieke_afsluiting_success(self, bfa_data):
        """
        provide a dict from the beweegbare_fysieke_afsluiting api and call
        the parser of the beweegbare_fysieke_afsluiting to get a sensor.
        call the import_sensor and expected it to be imported.
        """
        parser = import_utils_apis.parse_beweegbare_fysieke_afsluiting
        sensor_list = list(parser(bfa_data))
        sensor = sensor_list[0]
        person = sensor.owner
        imported_person = import_utils.import_person(person_data=person)
        result = import_utils.import_sensor(sensor, imported_person)
        created_sensor = result[0]
        assert str(created_sensor.type) == 'Feature'
        assert int(created_sensor.reference) == 11


@pytest.mark.django_db
class TestDeleteNotFoundSensor:
    """
    tests the delete sensor function. make sure it only deletes sensors that belong to the same
    owner and do not exist.
    """

    @property
    def actual(self):
        return [
            Device2Serializer(device).data
            for device in models.Device2.objects.all()
        ]

    def test_delete_one_sensor_from_three_sensors(self, wscm_data_delete):
        """provide three sensors to be created for the wifi sensor crowd management. after that provide
        only two same sensors to the delete_sensor function from the same owner. expect to have only
        two sensors remaining and one deleted."""
        parser = import_utils_apis.parse_wifi_sensor_crowd_management
        sensor_list = list(parser(wscm_data_delete))
        for sensor in sensor_list:
            person = sensor.owner
            imported_person = import_utils.import_person(person_data=person)
            import_utils.import_sensor(sensor, imported_person)

        assert len(self.actual) == 3

        # list of sensor objects for the delete function
        person = PersonData(
            organisation="Gemeente Amsterdam",
            email="LVMA@amsterdam.nl",
            telephone="06123456",
            website="https://acc.sensorenregister.amsterdam.nl",
            first_name="verkeers",
            last_name_affix="v",
            last_name="onderzoek"
        )

        sensor1 = SensorData(
            owner=person,
            reference=100,
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

        sensor2 = SensorData(
            owner=person,
            reference=101,
            type="Feature",
            location=LatLong(latitude=4.901853, longitude=52.3794284),
            datastream='',
            observation_goal='Tellen van mensen.',
            themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
            contains_pi_data='Ja',
            legal_ground='Verkeersmanagment in de rol van wegbeheerder.',
            privacy_declaration="https://www.amsterdam.nl/foo/",
            active_until='01-01-2050'
        )

        sensors_list = [sensor1, sensor2]
        import_utils_apis.delete_not_found_sendors(
            sensors=sensors_list,
            person=person
        )

        assert len(self.actual) == 2
        assert self.actual[0]['reference'] == '100'
        assert self.actual[1]['reference'] == '101'
        assert self.actual[0]['owner']['email'] == 'LVMA@amsterdam.nl'

    def test_delete_no_sensor_different_owner(self, wscm_data_delete):
        """provide three sensors to be created for the wifi sensor crowd management. after that provide
        only two same sensors to the delete_sensor function from the a different owner.
        expect to have no sensor deleted."""
        parser = import_utils_apis.parse_wifi_sensor_crowd_management
        sensor_list = list(parser(wscm_data_delete))
        for sensor in sensor_list:
            person = sensor.owner
            imported_person = import_utils.import_person(person_data=person)
            import_utils.import_sensor(sensor, imported_person)

        assert len(self.actual) == 3

        person = PersonData(
            organisation="Gemeente Amsterdam",
            email="verkeersonderzoek@amsterdam.nl",
            telephone="06123456",
            website="https://acc.sensorenregister.amsterdam.nl",
            first_name="verkeers",
            last_name_affix="v",
            last_name="onderzoek"
        )
        unknown_person = PersonData(
            organisation="Gemeente Amsterdam",
            email="someone@foo.nl",
            telephone="06123456",
            website="https://acc.sensorenregister.amsterdam.nl",
            first_name="verkeers",
            last_name_affix="v",
            last_name="onderzoek"
        )
        # list of sensor objects for the delete function
        sensor1 = SensorData(
            owner=person,
            reference=100,
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

        sensor2 = SensorData(
            owner=person,
            reference=101,
            type="Feature",
            location=LatLong(latitude=4.901853, longitude=52.3794284),
            datastream='',
            observation_goal='Tellen van mensen.',
            themes=settings.IPROX_SEPARATOR.join(['Mobiliteit: auto']),
            contains_pi_data='Ja',
            legal_ground='Verkeersmanagment in de rol van wegbeheerder.',
            privacy_declaration="https://www.amsterdam.nl/foo/",
            active_until='01-01-2050'
        )

        sensors_list = [sensor1, sensor2]
        import_utils_apis.delete_not_found_sendors(
            sensors=sensors_list,
            person=unknown_person
        )

        assert len(self.actual) == 3
        assert self.actual[0]['reference'] == '100'
        assert self.actual[1]['reference'] == '101'
        assert self.actual[2]['reference'] == '102'
        assert self.actual[0]['owner']['email'] == 'LVMA@amsterdam.nl'
