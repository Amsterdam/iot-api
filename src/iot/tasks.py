import logging

from django.conf import settings

from .celery import app
from .mail import send_confirmation_mail, send_mail_to_contact
from .models import Device

logger = logging.getLogger()


@app.task()
def send_iot_request(device_id, form_data, send_to_privacy_map=False):
    if send_to_privacy_map:
        device_reference = form_data['__link']
        device_contact_email = settings.AMSTERDAM_PRIVACY_MAP_EMAIL_ADDRESS
    else:
        try:
            device = Device.objects.get(pk=device_id)
            device_reference = device.reference
            device_contact_email = device.contact.email
        except Device.DoesNotExist:
            logger.error(
                'The device with PK #{} could not be found in the database'.format(device_id)
            )
            return

    context = {'device_reference': device_reference, 'form_data': form_data}

    # Send the request to the contact person of the IoT device
    send_mail_to_contact(device_contact_email, context)

    # Send confirmation mail that the request has been send
    send_confirmation_mail([form_data['email']], context)
