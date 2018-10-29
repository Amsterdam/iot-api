import logging

from .celery import app
from .mail import send_confirmation_mail, send_mail_to_contact
from .models import Device

logger = logging.getLogger()


@app.task()
def send_iot_request(device_id, form_data):
    try:
        device = Device.objects.get(pk=device_id)
    except Device.DoesNotExist:
        logger.error('The device with PK #{} could not be found in the database'.format(device_id))
        return

    context = {
        'device': device,
        'form_data': form_data,
    }

    # Send the request to the contact person of the IoT device
    send_mail_to_contact(device, context)

    # Send confirmation mail that the request has been send
    send_confirmation_mail([form_data['email']], device, context)
