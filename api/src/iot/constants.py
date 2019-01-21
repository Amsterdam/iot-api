from django.utils.translation import ugettext as _

FREQUENCY_CONTINUOUS = 'continuous'
FREQUENCY_PERIODIC = 'periodic'
FREQUENCY_INCIDENTAL = 'Incidental'

FREQUENCY_CHOICES = (
    (FREQUENCY_CONTINUOUS, _('Continue')),
    (FREQUENCY_PERIODIC, _('Periodiek')),
    (FREQUENCY_INCIDENTAL, _('Incidenteel')),
)

CATEGORY_CAMERA = 'CMR'
CATEGORY_SENSOR = 'SCP'
CATEGORY_BEACON = 'SBN'
CATEGORY_SMART_CHARGING_POLE = 'SCG'
CATEGORY_SMART_TRAFFIC_INFORMATION = 'STI'
CATEGORY_SMART_LAMPPOST = 'SLP'

CATEGORY_CHOICES = (
    (CATEGORY_CAMERA, _('Camera')),
    (CATEGORY_SENSOR, _('Sensor')),
    (CATEGORY_BEACON, _('Baken')),
    (CATEGORY_SMART_CHARGING_POLE, _('Slimme laadpaal')),
    (CATEGORY_SMART_TRAFFIC_INFORMATION, _('Slimme verkeersinformatie')),
    (CATEGORY_SMART_LAMPPOST, _('Slimme lantaarnpaal')),
)

QUEUE_STATUS_NEW = 'N'
QUEUE_STATUS_IN_PROGRESS = 'P'
QUEUE_STATUS_FAILED = 'F'
QUEUE_STATUS_DONE = 'D'

QUEUE_STATUSES = (
    (QUEUE_STATUS_NEW, 'New'),
    (QUEUE_STATUS_IN_PROGRESS, 'In progress'),
    (QUEUE_STATUS_FAILED, 'Failed'),
    (QUEUE_STATUS_DONE, 'Done'),
)
