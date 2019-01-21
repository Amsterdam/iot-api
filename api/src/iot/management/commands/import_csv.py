from __future__ import unicode_literals

import csv
from pathlib import Path

from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import Q

from iot.import_utils import CsvRow, CsvRowValidationException, import_row
from iot.mail import send_csv_import_report
from iot.models import Device, Person, Type
from iot.settings import settings


class Command(BaseCommand):
    """
    Import a CSV File into the database
    """
    help = 'Import a CSV file into the database, this will replace the currently loaded data'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **options):
        with transaction.atomic():
            if self._pre_handle(*args, **options):
                self._handle(*args, **options)
            self._post_handle(*args, **options)

    def _pre_handle(self, *args, **options):
        self.line_count = 0
        self.success = 0
        self._errors = []
        self.csv_file = Path(options['file_path'])
        self.validation_failed_for = []

        self.stdout.write('CSV File: {}'.format(self.csv_file))

        if not self.csv_file.exists() or not self.csv_file.is_file():
            self.csv_file = None
            return False

        with open(str(self.csv_file)) as csv_file:
            reader = csv.reader(csv_file)
            self.line_count = sum(1 for _ in reader) - 1

        return True

    def _handle(self, *args, **options):
        Device.objects.all().delete()

        self._print_progress(iteration=0, total=self.line_count)
        with open(str(self.csv_file)) as csv_file:
            reader = csv.reader(csv_file)
            next(reader)

            for count, row in enumerate(reader):
                try:
                    import_row(csv_row=CsvRow(*row))
                except CsvRowValidationException:
                    self._errors.append(row)
                self._print_progress(iteration=count+1, total=self.line_count)

    def _post_handle(self, *args, **options):
        # Remove unused types from the database
        Type.objects.filter(device__isnull=True).delete()

        # Remove unused Persons
        Person.objects.exclude(Q(owner__isnull=False) | Q(contact__isnull=False)).delete()

        if self._errors:
            self.stdout.write('Failed to import the following lines:')
            for _error in self._errors:
                self.stdout.write('* "{}"'.format('"," '.join(_error)))

        # Send csv import report
        send_csv_import_report(
            to=[settings.EMAIL, ],
            filename=self.csv_file.name if self.csv_file else 'unknown',
            imported=self.line_count-len(self._errors),
            errors=self._errors,
        )

        self.stdout.write('Done!')

    def _print_progress(self, iteration, total):
        percent = "{0:.1f}".format(100 * (iteration / float(total)))
        filled_length = int(100 * iteration // total)
        bar = '▋' * filled_length + '░' * (100 - filled_length)
        self.stdout.write('\r%s |%s| %s%% %s' % ('Progress', bar, percent, 'complete'), ending='\r')
        if iteration == total:
            self.stdout.write('')
