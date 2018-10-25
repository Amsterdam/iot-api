from django.utils.translation import ugettext as _

FREQUENCY_CONTINUOUS = 'continuous'
FREQUENCY_PERIODIC = 'periodic'
FREQUENCY_INCIDENTAL = 'Incidental'

FREQUENCY_CHOICES = (
    (FREQUENCY_CONTINUOUS, _('Continue')),
    (FREQUENCY_PERIODIC, _('Periodiek')),
    (FREQUENCY_INCIDENTAL, _('Incidenteel')),
)
