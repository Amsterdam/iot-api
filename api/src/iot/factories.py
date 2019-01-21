import random

import factory
import faker
from django.contrib.gis.geos import Point

from iot.constants import CATEGORY_CHOICES

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
        lambda o: '{0}'.format(fake.text(max_nb_chars=32))
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
        lambda o: '{},{}'.format(random.choice(CATEGORY_CHOICES)[0],
                                 random.choice(CATEGORY_CHOICES)[0])
    )
    geometrie = factory.LazyAttribute(
        lambda o: Point(4.58565, 52.03560)
    )
    owner = factory.SubFactory(PersonFactory)
    contact = factory.SubFactory(PersonFactory)

    class Meta:
        model = Device

    @factory.post_generation
    def types(self, create, extracted, **kwargs):
        if create or extracted:
            if extracted:
                for t in extracted:
                    self.types.add(t)
