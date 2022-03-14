from django.core.management.base import BaseCommand

from iot import import_utils_apis

API = 'https://maps.amsterdam.nl/open_geodata/geojson_lnglat.php?'
API_MAPPER = {
    'wifi_sensor_crowd_management': f'{API}KAARTLAAG=CROWDSENSOREN&THEMA=cmsa',
    'camera_brug_en_sluisbediening': f'{API}KAARTLAAG=PRIVACY_BRUGSLUIS&THEMA=privacy',
    # 'cctv_camera_verkeersmanagement': f'{API}KAARTLAAG=VIS&THEMA=vis',
    # 'kentekencamera_reistijd': f'{API}KAARTLAAG=VIS&THEMA=vis',
    # 'kentekencamera_milieuzone': f'{API}KAARTLAAG=VIS&THEMA=vis',
    # 'ais_masten': f'{API}KAARTLAAG=PRIVACY_AISMASTEN&THEMA=privacy',
    # 'verkeersonderzoek_met_cameras': f'{API}KAARTLAAG=PRIVACY_OVERIG&THEMA=privacy',
    # 'beweegbare_fysieke_afsluiting': f'{API}KAARTLAAG=VIS_BFA&THEMA=vis',
}


class Command(BaseCommand):
    """
    Used by the django manage app for executing a function using the command line.
    an argument can be provided with the name of the api to make an import only
    for that api. If no argument is given, all the apis in the api_mapper will
    be executed.
    """
    help = 'Imports Sensors data from APIs'

    def add_arguments(self, parser):
        parser.add_argument('api_name', nargs='+', type=str, help='provide the api_name')

    def handle(self, *args, **options):
        """
        has to be implemented. It will call the function that needs to
        be executed.
        """

        try:
            result_list = []  # empty list to save the apis results
            for api_name in options['api_name']:
                result = import_utils_apis.import_api_data(
                    api_name=api_name,
                    api_url=API_MAPPER[api_name]
                )
                result_list.append(result)  # append the import response as a tuple
            self.stdout.write(self.style.SUCCESS(f'API IMPORT RESULT: {result_list}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR_OUTPUT(f'API {e} NOT FOUND ERROR'))
