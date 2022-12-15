import pytest

from iot.importers import import_apis


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


class TestUrlAdjusterForLegalDeclarations:
    """
    tests for the adjust_url function that adds the https:// to the privacy_declaration
    url.
    """

    def test_adjust_url_with_https(self):
        """provide a url that starts with https://. expect the same url will be returned."""

        privacy_declaration_url = "https://www.amsterdam.nl/foo/"
        returned_url = import_apis.adjust_url(privacy_declaration_url)

        assert returned_url == privacy_declaration_url

    def test_adjust_url_without_https(self):
        """provide a url that doesn't starts with https://. expect the same
        url will be returned with https://."""

        privacy_declaration_url = "www.amsterdam.nl/foo/"
        expected_url = "https://www.amsterdam.nl/foo/"
        returned_url = import_apis.adjust_url(privacy_declaration_url)

        assert returned_url == expected_url

    def test_adjust_url_with_space(self):
        """provide a url that contains space at the end. expect the same
        url will be returned without space."""

        privacy_declaration_url = "https://www.amsterdam.nl/foo/ "
        expected_url = "https://www.amsterdam.nl/foo/"
        returned_url = import_apis.adjust_url(privacy_declaration_url)

        assert returned_url == expected_url
