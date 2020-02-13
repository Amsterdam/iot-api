import datetime
import random

import factory
import faker
from django.contrib.gis.geos import Point

from .constants import CATEGORY_CHOICES, FREQUENCY_CHOICES
from .models import Device, Person, Type

fake = faker.Faker()


class PersonFactory(factory.DjangoModelFactory):
    name = factory.LazyAttribute(
        lambda o: '{0}'.format(fake.name())
    )

    email = factory.LazyAttribute(
        lambda o: '{0}@amsterdam.nl'.format(o.name.replace(' ', '.').lower())
    )

    organisation = factory.LazyAttribute(
        lambda o: fake.company()
    )

    class Meta:
        model = Person


class TypeFactory(factory.DjangoModelFactory):
    name = factory.LazyAttribute(
        lambda o: fake.text(max_nb_chars=32)
    )

    application = factory.LazyAttribute(
        lambda o: fake.text(max_nb_chars=32)
    )

    description = factory.LazyAttribute(
        lambda o: fake.text(max_nb_chars=128)
    )

    class Meta:
        model = Type


class DeviceFactory(factory.DjangoModelFactory):
    reference = factory.LazyAttribute(
        lambda o: fake.text(max_nb_chars=32)
    )
    application = factory.LazyAttribute(
        lambda o: fake.text(max_nb_chars=32)
    )
    types = factory.SubFactory(TypeFactory)
    categories = factory.LazyAttribute(
        lambda o: f'{random.choice(CATEGORY_CHOICES)[0]},{random.choice(CATEGORY_CHOICES)[0]}')
    installation_point = factory.LazyAttribute(
        lambda o: fake.text(max_nb_chars=32)
    )
    frequency = factory.LazyAttribute(
        lambda o: random.choice(FREQUENCY_CHOICES)[0]
    )
    permit = bool(random.getrandbits(1))
    in_use_since = fake.date_object(end_datetime=datetime.datetime.now())
    postal_code = fake.text(max_nb_chars=6)
    house_number = fake.text(max_nb_chars=8)
    geometrie = factory.LazyAttribute(
        lambda o: Point(4.58565, 52.03560)
    )
    owner = factory.SubFactory(PersonFactory)
    contact = factory.SubFactory(PersonFactory)

    class Meta:
        model = Device

    @factory.post_generation
    def types(self, create, extracted, **kwargs):
        if extracted:
            for t in extracted:
                self.types.add(t)


def device_dict():
    return {
        "reference": fake.text(max_nb_chars=64),
        "application": fake.text(max_nb_chars=64),
        "types": [
            {
                "name": fake.text(max_nb_chars=64),
                "application": fake.text(max_nb_chars=64),
                "description": fake.text(max_nb_chars=200),
            },
            {
                "name": fake.text(max_nb_chars=64),
                "application": fake.text(max_nb_chars=64),
                "description": fake.text(max_nb_chars=200),
            },
            {
                "name": fake.text(max_nb_chars=64),
                "application": fake.text(max_nb_chars=64),
                "description": fake.text(max_nb_chars=200),
            }
        ],
        "categories": f'{random.choice(CATEGORY_CHOICES)[0]},{random.choice(CATEGORY_CHOICES)[0]}',
        "installation_point": fake.text(max_nb_chars=64),
        "frequency": random.choice(FREQUENCY_CHOICES)[0],
        "permit": bool(random.getrandbits(1)),
        "in_use_since": str(fake.date_object(end_datetime=datetime.datetime.now())),
        "postal_code": fake.text(max_nb_chars=6),
        "house_number": fake.text(max_nb_chars=8),
        "geometrie": {
            "longitude": 4.58565,
            "latitude": 52.0356
        },
        "privacy": fake.text(max_nb_chars=200),
        "owner": {
            "name": fake.text(max_nb_chars=8),
            "email": fake.email(),
            "organisation": fake.text(max_nb_chars=8),
        },
        "contact": {
            "name": fake.text(max_nb_chars=8),
            "email": fake.email(),
            "organisation": fake.text(max_nb_chars=8),
        },
    }
