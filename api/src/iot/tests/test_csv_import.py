import os
from io import StringIO

from django.core import mail, management
from django.test import TestCase, override_settings

from iot.import_utils import CsvRow, CsvRowValidationException, import_row
from iot.models import Device, Person, Type


class CsvImportTests(TestCase):
    def test_csv_import_long_lat(self):
        self.assertEqual(Device.objects.count(), 0)
        self.assertEqual(Type.objects.count(), 0)
        self.assertEqual(Person.objects.count(), 0)

        csv_row = CsvRow(
            'TST-123', 'Luchtmeting', 'NO2 meter', '', '', '4.90810', '52.36990', '', '',
            'O. wner', 'Organisation owner', 'owner@test.amsterdam.nl', 'C. ontact',
            'Organisation contact', 'contact@test.amsterdam.nl'
        )
        import_row(csv_row=csv_row)

        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(Type.objects.count(), 1)
        self.assertEqual(Person.objects.count(), 2)

    def test_csv_import_x_y(self):
        self.assertEqual(Device.objects.count(), 0)
        self.assertEqual(Type.objects.count(), 0)
        self.assertEqual(Person.objects.count(), 0)

        csv_row = CsvRow(
            'TST-123', 'Luchtmeting', 'NO2 meter', '110174', '490270', '', '', '', '',
            'O. wner', 'Organisation owner', 'owner@test.amsterdam.nl', 'C. ontact',
            'Organisation contact', 'contact@test.amsterdam.nl'
        )
        import_row(csv_row=csv_row)

        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(Type.objects.count(), 1)
        self.assertEqual(Person.objects.count(), 2)

    def test_csv_import_postalcode(self):
        self.assertEqual(Device.objects.count(), 0)
        self.assertEqual(Type.objects.count(), 0)
        self.assertEqual(Person.objects.count(), 0)

        csv_row = CsvRow(
            'TST-123', 'Luchtmeting', 'NO2 meter', '', '', '', '', '1013AW', '',
            'O. wner', 'Organisation owner', 'owner@test.amsterdam.nl', 'C. ontact',
            'Organisation contact', 'contact@test.amsterdam.nl'
        )
        import_row(csv_row=csv_row)

        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(Type.objects.count(), 1)
        self.assertEqual(Person.objects.count(), 2)

    def test_csv_import_no_types(self):
        self.assertEqual(Device.objects.count(), 0)
        self.assertEqual(Type.objects.count(), 0)
        self.assertEqual(Person.objects.count(), 0)

        csv_row = CsvRow(
            'TST-123', 'Luchtmeting', '', '', '', '4.90810', '52.36990', '', '',
            'O. wner', 'Organisation owner', 'owner@test.amsterdam.nl', 'C. ontact',
            'Organisation contact', 'contact@test.amsterdam.nl'
        )
        import_row(csv_row=csv_row)

        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(Type.objects.count(), 0)
        self.assertEqual(Person.objects.count(), 2)

    def test_csv_import_invalid_data(self):
        self.assertEqual(Device.objects.count(), 0)
        self.assertEqual(Type.objects.count(), 0)
        self.assertEqual(Person.objects.count(), 0)

        csv_row = CsvRow(
            'TST-123', 'Luchtmeting', 'NO2 meter', '', '', '', '', '', '',
            '', 'Organisation owner', 'not an email', '', 'Organisation contact', 'not an email'
        )
        self.assertRaises(CsvRowValidationException, import_row, csv_row=csv_row)

        self.assertEqual(Device.objects.count(), 0)
        self.assertEqual(Type.objects.count(), 0)
        self.assertEqual(Person.objects.count(), 0)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_command(self):
        mail.outbox = []

        self.assertEqual(Device.objects.count(), 0)
        self.assertEqual(Type.objects.count(), 0)
        self.assertEqual(Person.objects.count(), 0)

        out = StringIO()
        management.call_command('import_csv',
                                os.path.abspath('./iot/tests/csv_import/valid_test.csv'),
                                stdout=out)

        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(Type.objects.count(), 1)
        self.assertEqual(Person.objects.count(), 2)

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.subject, 'CSV Import rapportage voor bestand valid_test.csv')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_command_with_invalid_row(self):
        mail.outbox = []

        self.assertEqual(Device.objects.count(), 0)
        self.assertEqual(Type.objects.count(), 0)
        self.assertEqual(Person.objects.count(), 0)

        out = StringIO()
        management.call_command('import_csv',
                                os.path.abspath('./iot/tests/csv_import/invalid_test.csv'),
                                stdout=out)

        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(Type.objects.count(), 1)
        self.assertEqual(Person.objects.count(), 2)

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.subject, 'CSV Import rapportage voor bestand invalid_test.csv')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_command_invalid_file(self):
        self.assertEqual(Device.objects.count(), 0)
        self.assertEqual(Type.objects.count(), 0)
        self.assertEqual(Person.objects.count(), 0)

        out = StringIO()
        management.call_command('import_csv', 'thisdoesnotexdistsatall.csv', stdout=out)

        self.assertEqual(Device.objects.count(), 0)
        self.assertEqual(Type.objects.count(), 0)
        self.assertEqual(Person.objects.count(), 0)
