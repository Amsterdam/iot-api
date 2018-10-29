from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template


def send_mail_to_contact(device, context={}):
    to = [device.contact.email, ]
    context.update({'device': device, })

    subject = 'Requested use for IoT device reference {}'.format(device.reference)
    txt_message = get_template('email/contact_iot_owner.txt').render(context)
    html_message = get_template('email/contact_iot_owner.html').render(context)

    return send_mail(
        subject=subject,
        message=txt_message,
        html_message=html_message,
        from_email=settings.NOREPLY,
        recipient_list=to,
        fail_silently=False
    )


def send_confirmation_mail(to, device, context={}):
    context.update({'device': device, })

    subject = 'Confirmation about request to use IoT device reference {}'.format(device.reference)
    txt_message = get_template('email/confirm_iot_request.txt').render(context)
    html_message = get_template('email/confirm_iot_request.html').render(context)

    return send_mail(
        subject=subject,
        message=txt_message,
        html_message=html_message,
        from_email=settings.NOREPLY,
        recipient_list=to,
        fail_silently=False
    )
