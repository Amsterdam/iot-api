from __future__ import unicode_literals

import requests
from django.core.management import BaseCommand

from iot.models import Address, Device, Location, Type
from iot.settings import settings


class Command(BaseCommand):
    """
    Temporary import script to provide some mocked data for the front end developer
    Must be deleted after the real import has been build
    """
    help = 'Import VSD into acceptance/local database (will not run on production)'

    def handle(self, *args, **options):
        self.stdout.write('Import VSD into acceptance/local database')
        if settings.SECRET_KEY != settings.INSECURE_SECRET_KEY:
            self.stdout.write('Running the Import VSD command in production is not allowed')
            return

        self.import_vsd()

    def import_vsd(self):
        data = self.get_all_data()
        self.create_objects(*data)

    def create_objects(self, set_1, set_2, set_3):
        for iot_thing in set_1:
            iot_type, _ = Type.objects.get_or_create(
                name=iot_thing['device_type'],
                defaults={'application': iot_thing['device_type'],
                          'description': iot_thing['device_type']},
            )

            loc = [item for item in set_3 if item['thing_id'] == iot_thing['id']][0]
            marker = [item for item in set_2 if item['location_id'] == loc['id']][0]
            location, _ = Location.objects.get_or_create(
                latitude=marker['wgs84_geometry']['coordinates'][0],
                longitude=marker['wgs84_geometry']['coordinates'][1],
            )
            address, _ = Address.objects.get_or_create(street=loc['name'])

            device, created = Device.objects.get_or_create(
                reference=iot_thing['ref'],
                defaults=dict(
                    application=iot_thing['purpose'] or iot_thing['description'],
                    address=address,
                    location=location,
                )
            )

            if created:
                device.types.add(iot_type)
                device.save()

                self.stdout.write('Imported device with id #{}'.format(device.pk))
            else:
                self.stdout.write('Device with id #{} was already imported'.format(device.pk))

    def get_all_data(self):
        self.stdout.write('Get data from VSD')
        urls = [
            'https://api.data.amsterdam.nl/vsd/iot_things',
            'https://api.data.amsterdam.nl/vsd/iot_markers',
            'https://api.data.amsterdam.nl/vsd/iot_locations'
        ]

        all_data = []
        for url in urls:
            all_data.append(self.get_data(url=url))

        return all_data

    def get_data(self, url):
        params = {'page': 1, 'page_size': 50}
        response = requests.get(url, params=params)
        data = response.json()
        return data['results']
