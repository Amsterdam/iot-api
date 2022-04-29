from io import StringIO

import pytest
from django.core.management import call_command
from django.test import TestCase


class ImportApiTest(TestCase):
    """
    tests for the django manager app for command line calls.
    """

    def test_command_import_api_output_not_found_api(self):
        """
        call the import_api command with an unknown api_name and expect an exception to be raised.
        """
        with StringIO() as out:
            with pytest.raises(Exception):
                call_command('import_api', 'something', stdout=out)
