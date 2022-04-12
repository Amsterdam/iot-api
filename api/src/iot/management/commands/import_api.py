from django.core.management.base import BaseCommand

from iot import import_utils_apis


class Command(BaseCommand):
    """
    Used by the django manage app for executing a function using the command line.
    an argument should be provided with the name of the api to make an import only
    for that api. it can also take a list of apis and all will be execute. The current
    available apis are:
    wifi_sensor_crowd_management
    sensor_crowd_management
    camera_brug_en_sluisbediening
    cctv_camera_verkeersmanagement
    kentekencamera_reistijd
    kentekencamera_milieuzone
    ais_masten
    verkeersonderzoek_met_cameras
    beweegbare_fysieke_afsluiting
    """
    help = 'Imports Sensors data from APIs.To exeucting it: python manage.py import_api api1 api2'

    def add_arguments(self, parser):
        parser.add_argument('api_name', nargs='*', type=str, help='provide the api_name')

    def handle(self, *args, **options):
        """
        has to be implemented. It will call the function that needs to
        be executed with an optional list of api_name as args.
        """
        result = import_utils_apis.import_api_data(api_names=options['api_name'])

        self.stdout.write(self.style.SUCCESS(f'{result}'))
