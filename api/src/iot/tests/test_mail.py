from django.core import mail
from django.test import TestCase, override_settings

from ..factories import DeviceFactory
from ..mail import send_confirmation_mail, send_mail_to_contact
from ..tasks import send_iot_request


class MailTestCase(TestCase):
    def setUp(self):
        self.device = DeviceFactory.create()

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_mail_to_contact(self):
        mail.outbox = []

        context = {'device_reference': self.device.reference}
        send_mail_to_contact(email_address=self.device.contact.email, context=context)

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]

        self.assertEqual(
            message.subject,
            'Requested use for IoT device reference {}'.format(
                self.device.reference
            )
        )

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_confirmation_mail(self):
        mail.outbox = []

        context = {'device_reference': self.device.reference}
        send_confirmation_mail(to=['test@test.com'], context=context)

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]

        self.assertEqual(
            message.subject,
            'Confirmation about request to use IoT device reference {}'.format(
                self.device.reference
            )
        )

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_task_send_iot_request(self):
        mail.outbox = []

        data = {'email': 'test@test.com', }
        send_iot_request(device_id=self.device.pk, form_data=data)

        self.assertEqual(len(mail.outbox), 2)

        subjects = [
            'Requested use for IoT device reference {}'.format(
                self.device.reference
            ),
            'Confirmation about request to use IoT device reference {}'.format(
                self.device.reference
            )
        ]

        for message in mail.outbox:
            self.assertIn(message.subject, subjects)

    @override_settings(CELERY_EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_task_send_iot_request_non_existing_device(self):
        mail.outbox = []

        data = {'email': 'test@test.com', }
        send_iot_request(device_id=99999999, form_data=data)

        self.assertEqual(len(mail.outbox), 0)
