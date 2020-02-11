from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..factories import DeviceFactory, TypeFactory, device_dict
from ..models import Device


class PingTestCase(APITestCase):
    def test_index_pages(self):
        url = reverse('ping')
        response = self.client.get(url)

        self.assertEqual(
            status.HTTP_200_OK, response.status_code, 'Wrong response code for {}'.format(url)
        )


class DeviceTestCase(APITestCase):
    # Credentials for a user which will have all authorizations
    USERNAME = "user1"
    EMAIL = 'a@b.com'
    PASSWORD = "password1"

    def compare_geometrie(self, k, last_record_in_db, device_input):
        self.assertEqual(last_record_in_db.geometrie.y, device_input[k]['latitude'])
        self.assertEqual(last_record_in_db.geometrie.x, device_input[k]['longitude'])

    def compare_in_use_since(self, k, last_record_in_db, device_input):
        self.assertEqual(str(getattr(last_record_in_db, k)), device_input[k])

    def compare_categories(self, k, last_record_in_db, device_input):
        self.assertEqual(device_input[k].split(','), last_record_in_db.categories.split(","))

    def compare_types(self, k, last_record_in_db, device_input):
        self.assertEqual(len(device_input[k]), last_record_in_db.types.all().count())

    def compare_owner(self, k, last_record_in_db, device_input):
        # From the owner we disregard everything except the organisation
        self.assertEqual(last_record_in_db.owner.organisation, device_input[k]['organisation'])

    def compare_contact(self, k, last_record_in_db, device_input):
        for contact_attr in device_input[k].keys():
            self.assertEqual(
                device_input[k][contact_attr],
                getattr(last_record_in_db.contact, contact_attr)
            )

    def compare_other(self, k, last_record_in_db, device_input):
        self.assertEqual(getattr(last_record_in_db, k), device_input[k])

    def setUp(self):
        self.slimme_app_group, _ = Group.objects.get_or_create(
            name=settings.KEYCLOAK_SLIMMEAPPARATEN_WRITE_PERMISSION_NAME)
        self.authorized_user = User.objects.create_user(self.USERNAME, self.EMAIL, self.PASSWORD)
        self.slimme_app_group.user_set.add(self.authorized_user)

        self.RESULT_TESTS = {
            'geometrie': self.compare_geometrie,
            'in_use_since': self.compare_in_use_since,
            'categories': self.compare_categories,
            'types': self.compare_types,
            'owner': self.compare_owner,
            'contact': self.compare_contact
        }

    def test_list(self):
        url = reverse('device-list')
        response = self.client.get(url)

        self.assertEqual(
            status.HTTP_200_OK, response.status_code, 'Wrong response code for {}'.format(url)
        )

        data = response.json()

        self.assertEqual(0, data['count'])
        self.assertEqual(0, len(data['results']))
        self.assertIsNone(data['_links']['next']['href'])
        self.assertIsNone(data['_links']['previous']['href'])

    def test_list_1_item(self):
        device = DeviceFactory.create()

        url = reverse('device-list')
        response = self.client.get(url)

        self.assertEqual(
            status.HTTP_200_OK, response.status_code, 'Wrong response code for {}'.format(url)
        )

        data = response.json()

        self.assertEqual(1, data['count'])
        self.assertEqual(1, len(data['results']))

        self.assertEqual(device.reference, data['results'][0]['reference'])
        self.assertEqual(device.application, data['results'][0]['application'])
        self.assertEqual(len(device.categories.split(",")), len(data['results'][0]['categories']))
        self.assertAlmostEqual(float(device.geometrie.x),
                               float(data['results'][0]['longitude']))
        self.assertAlmostEqual(float(device.geometrie.y),
                               float(data['results'][0]['latitude']))
        self.assertEqual(device.owner.organisation, data['results'][0]['organisation'])

    def test_list_pagination(self):
        DeviceFactory.create_batch(9)

        t = TypeFactory.create()
        DeviceFactory.create(types=[t, ])

        url = '{}?page_size=5'.format(reverse('device-list'))
        response = self.client.get(url)

        self.assertEqual(
            status.HTTP_200_OK, response.status_code, 'Wrong response code for {}'.format(url)
        )

        data = response.json()

        self.assertEqual(10, data['count'])
        self.assertEqual(5, len(data['results']))

        self.assertIsNotNone(data['_links']['next']['href'])
        self.assertIsNone(data['_links']['previous']['href'])

        response = self.client.get(data['_links']['next']['href'])

        self.assertEqual(
            status.HTTP_200_OK, response.status_code, 'Wrong response code for {}'.format(url)
        )

        data = response.json()

        self.assertEqual(10, data['count'])
        self.assertEqual(5, len(data['results']))

        self.assertIsNone(data['_links']['next']['href'])
        self.assertIsNotNone(data['_links']['previous']['href'])

    def test_detail_not_logged_in(self):
        device = DeviceFactory.create()

        url = reverse('device-detail', kwargs={'pk': device.pk})
        response = self.client.get(url)

        self.assertEqual(
            status.HTTP_200_OK, response.status_code, 'Wrong response code for {}'.format(url)
        )

        data = response.json()

        self.assertEqual(device.reference, data['reference'])
        self.assertEqual(device.application, data['application'])
        self.assertEqual(len(device.categories.split(",")), len(data['categories']))
        self.assertAlmostEqual(float(device.geometrie.x), float(data['longitude']))
        self.assertAlmostEqual(float(device.geometrie.y), float(data['latitude']))
        self.assertEqual(device.owner.organisation, data['organisation'])
        self.assertEqual(data.get('owner'), None)
        self.assertEqual(data.get('contact'), None)

    # We explicitly remove the SessionRefresh middleware because it will respond with redirects
    # to check the validity of our tokens. That fails our tests, and is out of the scope of this test.
    @override_settings(
        MIDDLEWARE=[mc for mc in settings.MIDDLEWARE if mc != 'mozilla_django_oidc.middleware.SessionRefresh']
    )
    def test_detail_logged_in_not_owned(self):
        """ Tests getting a resource which is not owned by the logged in user """
        device = DeviceFactory.create()

        url = reverse('device-detail', kwargs={'pk': device.pk})

        self.client.force_login(self.authorized_user)
        response = self.client.get(url)
        self.client.logout()

        self.assertEqual(
            status.HTTP_200_OK, response.status_code, 'Wrong response code for {}'.format(url)
        )

        data = response.json()

        self.assertEqual(device.reference, data['reference'])
        self.assertEqual(device.application, data['application'])
        self.assertEqual(len(device.categories.split(",")), len(data['categories']))
        self.assertAlmostEqual(float(device.geometrie.x), float(data['longitude']))
        self.assertAlmostEqual(float(device.geometrie.y), float(data['latitude']))
        self.assertEqual(device.owner.organisation, data['organisation'])
        self.assertEqual(data.get('owner'), None)
        self.assertEqual(data.get('contact'), None)

    # We explicitly remove the SessionRefresh middleware because it will respond with redirects
    # to check the validity of our tokens. That fails our tests, and is out of the scope of this test.
    @override_settings(
        MIDDLEWARE=[mc for mc in settings.MIDDLEWARE if mc != 'mozilla_django_oidc.middleware.SessionRefresh']
    )
    def test_detail_logged_in_and_owned(self):
        """ Tests getting a resource which is owned by the logged in user """
        device = DeviceFactory.create()
        device.owner.email = self.EMAIL
        device.owner.save()

        url = reverse('device-detail', kwargs={'pk': device.pk})

        self.client.force_login(self.authorized_user)
        response = self.client.get(url)
        self.client.logout()

        self.assertEqual(status.HTTP_200_OK, response.status_code, 'Wrong response code for {}'.format(url))

        data = response.json()

        self.assertEqual(device.reference, data['reference'])
        self.assertEqual(device.application, data['application'])
        self.assertEqual(len(device.categories.split(",")), len(data['categories']))
        self.assertAlmostEqual(float(device.geometrie.x), float(data['longitude']))
        self.assertAlmostEqual(float(device.geometrie.y), float(data['latitude']))
        self.assertEqual(device.owner.organisation, data['organisation'])
        self.assertEqual(data['owner']['email'], device.owner.email)
        self.assertNotEqual(data['contact'], None)

    def test_minimal_post_fails_when_not_logged_in(self):
        device = DeviceFactory.build()
        device_count_before = Device.objects.all().count()

        url = reverse('device-list')
        self.client.logout()  # Make sure the user is logged out
        response = self.client.post(
            url,
            data={
                "reference": device.reference,
                "application": device.application,
                "types": [],
                "categories": "SLP,CMR",
                "owner": {"name": "Jan", "email": "a@b.com", "organisation": "organisation name"}
            },
            format='json'
        )

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(device_count_before, Device.objects.all().count())

    def test_minimal_post(self):
        device = DeviceFactory.build()
        device_count_before = Device.objects.all().count()

        url = reverse('device-list')
        self.client.force_login(self.authorized_user)
        response = self.client.post(
            url,
            data={
                "reference": device.reference,
                "application": device.application,
                "types": [],
                "categories": "SLP,CMR",
                "owner": {"name": "Jan", "email": "a@b.com", "organisation": "organisation name"}
            },
            format='json'
        )
        self.client.logout()

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(device_count_before + 1, Device.objects.all().count())

        last_record_in_db = Device.objects.all().order_by('-id')[:1][0]
        self.assertEqual(last_record_in_db.reference, device.reference)
        self.assertEqual(last_record_in_db.application, device.application)
        self.assertEqual(last_record_in_db.types.count(), 0)

    def test_full_post(self):
        device_count_before = Device.objects.all().count()

        device_input = device_dict()
        url = reverse('device-list')
        self.client.force_login(self.authorized_user)
        response = self.client.post(
            url,
            data=device_input,
            format='json'
        )
        self.client.logout()

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(device_count_before + 1, Device.objects.all().count())
        last_record_in_db = Device.objects.all().order_by('-id')[:1][0]
        self.assertEqual(last_record_in_db.owner.email, self.authorized_user.email)

        for k in device_input.keys():
            self.RESULT_TESTS.get(k, self.compare_other)(k, last_record_in_db, device_input)

    def test_put(self):
        device = DeviceFactory.create()

        url = reverse('device-detail', kwargs={'pk': device.pk})
        self.client.force_login(self.authorized_user)
        response = self.client.put(url, data={})
        self.client.logout()

        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_delete(self):
        device = DeviceFactory.create()

        url = reverse('device-detail', kwargs={'pk': device.pk})
        self.client.force_login(self.authorized_user)
        response = self.client.delete(url)
        self.client.logout()

        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)


class ContactTestCase(APITestCase):
    def setUp(self):
        self.device = DeviceFactory.create()

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                       task_always_eager=True)
    def test_contact(self):
        mail.outbox = []
        url = reverse('contact-list')
        data = {
            'device': self.device.pk,
            'name': 'T. Est',
            'email': 'test@amsterdam.nl',
        }

        response = self.client.post(url, data=data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
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

    def test_contact_invalid_data(self):
        url = reverse('contact-list')
        data = {
            'device': self.device.pk,
            # 'name': 'T. Est',  # The name is required
            'email': 'this is not an email address',
        }

        response = self.client.post(url, data=data)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_contact_device_does_not_exists(self):
        url = reverse('contact-list')
        data = {
            'device': 666,
            'name': 'T. Est',
            'email': 'test@amsterdam.nl',
        }

        response = self.client.post(url, data=data)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
