import random

import factory
import faker

from iot.constants import CATEGORY_CHOICES

from .models import Address, Device, Location, Person, Type

fake = faker.Faker()


class AddressFactory(factory.DjangoModelFactory):
    street = factory.LazyAttribute(
        lambda o: fake.street_name()
    )

    house_number = factory.LazyAttribute(
        lambda o: random.randint(0, 100)
    )

    postal_code = factory.LazyAttribute(
        lambda o: fake.postcode()
    )

    city = factory.LazyAttribute(
        lambda o: fake.city()
    )

    municipality = 'Amsterdam'

    country = factory.LazyAttribute(
        lambda o: fake.country_code()
    )

    class Meta:
        model = Address


class LocationFactory(factory.DjangoModelFactory):
    longitude = factory.LazyAttribute(
        lambda o: fake.longitude()
    )
    latitude = factory.LazyAttribute(
        lambda o: fake.latitude()
    )

    class Meta:
        model = Location


class PersonFactory(factory.DjangoModelFactory):
    name = factory.LazyAttribute(
        lambda o: '{0}'.format(fake.name())
    )

    email = factory.LazyAttribute(
        lambda o: '{0}@amsterdam.nl'.format(o.name)
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

    address = factory.SubFactory(AddressFactory)
    location = factory.SubFactory(LocationFactory)

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
