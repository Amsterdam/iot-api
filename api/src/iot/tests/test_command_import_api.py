from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class ImportApiTest(TestCase):
    """
    tests for the django manager app for command line calls.
    """

    def test_command_import_api_output_not_found_api(self):
        """
        call the import_api command with an unknown api_name and expect a tuple
        converted to a string with the first element is a list of the error.
        """
        with StringIO() as out:
            call_command('import_api', 'something', stdout=out)
            expected_err_contains = 'something'
            output = out.getvalue()
            self.assertIn(expected_err_contains, output)
