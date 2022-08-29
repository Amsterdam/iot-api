import requests
from django.contrib.gis.geos import Polygon
from django.core.management import BaseCommand
from rest_framework_gis.fields import GeometryField

from iot.import_utils import (
    LatLong,
    Location,
    ObservationGoal,
    PersonData,
    SensorData,
    import_person,
    import_sensor,
)


def get(url, **params):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


parse_geometry = GeometryField().to_internal_value


def get_parking_zone_polygons():
    url = "https://amsterdam-maps.bma-collective.com/embed/parkeren/deploy_data/tarieven.json"
    parking_zones = get(url).values()
    return [
        parse_geometry(zone["location"])
        for zone in parking_zones
    ]


def get_neighbourhoods():
    url = "https://maps.amsterdam.nl/open_geodata/geojson_lnglat.php"
    neighbourhoods = get(url, KAARTLAAG="INDELING_BUURT", THEMA="gebiedsindeling")["features"]
    return {
        neighbourhood["properties"]["Buurtcode"]: parse_geometry(
            neighbourhood["geometry"]
        )
        for neighbourhood in neighbourhoods
    }


class Command(BaseCommand):
    def handle(self, *args, **options):

        parking_neighbourhood = Polygon()
        parking_neighbourhood_codes = []

        neighbourhoods = get_neighbourhoods()
        for parking_zone_polygon in get_parking_zone_polygons():

            for neighbourhood_code, neighbourhood_polygon in neighbourhoods.items():

                parking_zone_polygons = (
                    [parking_zone_polygon]
                    if isinstance(parking_zone_polygon, Polygon)
                    else parking_zone_polygon
                )

                # if there is any overlap between this neighbourhood polygoon and the
                # parking polygon we say that the scan auto will be driving in this
                # neighbourhood
                if any(map(neighbourhood_polygon.intersects, parking_zone_polygons)):
                    parking_neighbourhood = parking_neighbourhood.union(
                        neighbourhood_polygon
                    )
                    parking_neighbourhood_codes.append(neighbourhood_code)

        sensor = SensorData(
            owner=PersonData(
                organisation="Gemeente Amsterdam",
                email="parkeerdata@amsterdam.nl",
                telephone="14020",
                website="https://amsterdam.nl",
                first_name="Afdeling",
                last_name_affix="",
                last_name="Parkeren, Team Analyse & Advies",
            ),
            reference="parkeer_scan_auto",
            type="Optische / camera sensor",
            location=Location(
                lat_long=LatLong(
                    latitude=parking_neighbourhood.centroid[1],
                    longitude=parking_neighbourhood.centroid[0],
                ),
                postcode_house_number=None,
                description="",
                regions=";".join(parking_neighbourhood_codes),
            ),
            datastream="Gescande afbeeldingen van kentekenplaten, samen met de locatie van de auto en tijdstempelgegevens.",
            observation_goals=[
                ObservationGoal(
                    observation_goal="De uitvoering van een taak van algemeen belang",
                    legal_ground="Het uitvoeren van het gemeentelijk parkeerbeleid op basis van artikel 225 van de Gemeentewet",
                    privacy_declaration="https://www.amsterdam.nl/privacy/specifieke/privacyverklaring-parkeren-verkeer-bouw/straatparkeren/",
                ),
            ],
            themes="Mobiliteit",
            contains_pi_data="Ja",
            active_until="01-01-2050",
            projects=["Gemeente Amsterdam"],
        )

        owner = import_person(sensor.owner)
        import_sensor(sensor, owner)
