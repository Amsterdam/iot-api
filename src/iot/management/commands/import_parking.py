from contextlib import suppress

import requests
from django.contrib.gis.geos import Polygon
from rest_framework_gis.fields import GeometryField


def get(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


parse_geometry = GeometryField().to_internal_value


def get_parking_zones():
    url = 'https://amsterdam-maps.bma-collective.com/embed/parkeren/deploy_data/tarieven.json'
    parking_zones = get(url).values()
    return (parse_geometry(zone['location']) for zone in parking_zones)


def get_neighbourhoods():
    url = 'https://maps.amsterdam.nl/open_geodata/geojson_lnglat.php?KAARTLAAG=INDELING_BUURT&THEMA=gebiedsindeling'
    neighbourhoods = get(url)['features']
    return {
        neighbourhood['properties']['Buurtcode']: parse_geometry(
            neighbourhood['geometry']
        )
        for neighbourhood in neighbourhoods
    }


neighbourhoods = get_neighbourhoods()


parking_neighbourhood = Polygon()

for parking_polygon in get_parking_zones():
    for code, neighbourhood_polygon in neighbourhoods.items():
        with suppress(Exception):
            if neighbourhood_polygon.centroid.within(parking_polygon.convex_hull):
                parking_neighbourhood = parking_neighbourhood.union(
                    neighbourhood_polygon
                )

with open('combined.kml', 'w') as f:
    f.write(parking_neighbourhood.kml)
