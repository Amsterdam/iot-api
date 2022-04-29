import requests
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

    def handle(self, *args, **options) -> str:
        """
        takes a list of the name(s) of the api as a param, calls the url that belongs to it in the
        API_MAPPER. when the data is fetched from the api, it will convert it to a dict
        and pass it to the convert_api_data together with the api_name.
        A tuple will be returned that will contain the results. The results will be a list dict
        for each api's result of inserts, updates and errors.
        """
        # if the list api_names is an empty list, copy the list of all the api_names (keys)
        # from the API_MAPPER dict so the api_names will contain a list of all the api_name
        # from the API_MAPPER dictionary, else use the app_names list with the provided
        # app_names list.

        api_names = options['api_name']
        if not api_names:
            api_names = import_utils_apis.API_MAPPER.keys()

        for api in api_names:
            api_url = import_utils_apis.API_MAPPER[api]  # get the url that belongs to the api.

            response = requests.get(url=api_url)
            # check if response is 200 and content type is json, if not, return
            if response.status_code != 200 or \
                    'application/json' not in response.headers["Content-Type"]:
                raise RuntimeError(f"{response.status_code} - {response.content}")

            data = response.json()  # get the content of the response as dict
            result = import_utils_apis.convert_api_data(api_name=api, api_data=data)
            # convert the out to a str with inserts, updates and errors
            output = f'{api}: inserts {result[1]}, updates {result[2]}, errors {len(result[0])}'

            self.stdout.write(self.style.SUCCESS(f'{output}'))
