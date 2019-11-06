from django.core import mail, serializers
from django.test import override_settings
from django.urls import reverse
from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.test import APITestCase

from iot.factories import DeviceFactory, TypeFactory
from iot.models import Device


class PingTestCase(APITestCase):
    def test_index_pages(self):
        url = reverse('ping')
        response = self.client.get(url)

        self.assertEqual(
            status.HTTP_200_OK, response.status_code, 'Wrong response code for {}'.format(url)
        )


class DeviceTestCase(APITestCase):
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
        self.assertEqual(len(device.categories.split(',')), len(data['results'][0]['categories']))
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

    def test_detail(self):
        device = DeviceFactory.create()

        url = reverse('device-detail', kwargs={'pk': device.pk})
        response = self.client.get(url)

        self.assertEqual(
            status.HTTP_200_OK, response.status_code, 'Wrong response code for {}'.format(url)
        )

        data = response.json()

        self.assertEqual(device.reference, data['reference'])
        self.assertEqual(device.application, data['application'])
        self.assertEqual(len(device.categories.split(',')), len(data['categories']))
        self.assertAlmostEqual(float(device.geometrie.x), float(data['longitude']))
        self.assertAlmostEqual(float(device.geometrie.y), float(data['latitude']))
        self.assertEqual(device.owner.organisation, data['organisation'])

    def test_minimal_post(self):
        device = DeviceFactory.build()
        device_count_before = Device.objects.all().count()

        url = reverse('device-list')
        response = self.client.post(
            url,
            data={"reference": device.reference, "application": device.application, "types": []},
            format='json'
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(device_count_before + 1, Device.objects.all().count())

        last_record_in_db = Device.objects.all().order_by('-id')[:1][0]
        self.assertEqual(last_record_in_db.reference, device.reference)
        self.assertEqual(last_record_in_db.application, device.application)
        self.assertEqual(last_record_in_db.types.count(), 0)

    def test_full_post(self):
        device = DeviceFactory.create()
        for i in range(3):
            device.types.add(TypeFactory.create())

        device_count_before = Device.objects.all().count()

        device_dict = model_to_dict(device)

        ##### Convert model to DICT ####
        # Remove the id
        del device_dict['id']

        # Convert point to lat/long

        device_dict['geometrie'] = {
            'longitude': device_dict['geometrie'].x,
            'latitude': device_dict['geometrie'].y
        }
        # del device_dict['geometrie']

        # Add the types as json objects instead of ints
        new_types = []
        for m in device_dict['types']:
            new_types.append(model_to_dict(m))
            del new_types[-1]['id']
        device_dict['types'] = new_types

        ##### Convert model to DICT ####


        url = reverse('device-list')
        response = self.client.post(
            url,
            data=device_dict,
            format='json'
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(device_count_before + 1, Device.objects.all().count())
        last_record_in_db = Device.objects.all().order_by('-id')[:1][0]

        for k in device_dict.keys():
            if k == 'geometrie':
                self.assertEqual(last_record_in_db.geometrie.y, device_dict[k]['latitude'])
                self.assertEqual(last_record_in_db.geometrie.x, device_dict[k]['longitude'])
                continue

            if k in ('types', 'categories', 'owner', 'contact'):
                # print("======D", k, getattr(last_record_in_db, k), device_dict[k])
                # self.assertEqual(getattr(last_record_in_db, k).count(), len(device_dict[k]))
                # for categorie in device_dict[k]:
                #     self.assertEqual(getattr(last_record_in_db, k)[0], categorie)
                # continue
                continue

            self.assertEqual(getattr(last_record_in_db, k), device_dict[k])

    def test_put(self):
        device = DeviceFactory.create()

        url = reverse('device-detail', kwargs={'pk': device.pk})
        response = self.client.put(url, data={})

        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_delete(self):
        device = DeviceFactory.create()

        url = reverse('device-detail', kwargs={'pk': device.pk})
        response = self.client.delete(url)

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
