from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class ImportApiTest(TestCase):
    """
    tests for the django manager app for command line calls.
    """

    def test_command_import_api_output_not_found_api(self):
        """
        call the import_api command with an unknown api_name and expect the below expected string.
        """
        out = StringIO()
        call_command('import_api', 'something', stdout=out)
        expected_err = 'unknown api_name something'
        error = out.getvalue()
        self.assertIn(expected_err, error)

    def test_command_import_api_output_no_args_raise_exception(self):
        """
        call the import_api command and expect the below expected string.
        """
        out = StringIO()
        with pytest.raises(CommandError):
            call_command('import_api', stdout=out)
