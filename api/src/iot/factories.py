import random

import factory
import faker

from .models import Address, Device, Person, Type

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


class PersonFactory(factory.DjangoModelFactory):
    name = factory.LazyAttribute(
        lambda o: '{0}'.format(fake.name())
    )

    email = factory.LazyAttribute(
        lambda o: '{0}@amsterdam.nl'.format(o.name)
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
    type = factory.SubFactory(TypeFactory)

    address = factory.SubFactory(AddressFactory)
    longitude = factory.LazyAttribute(
        lambda o: fake.longitude()
    )
    latitude = factory.LazyAttribute(
        lambda o: fake.latitude()
    )

    organisation = factory.LazyAttribute(
        lambda o: fake.company()
    )
    owner = factory.SubFactory(PersonFactory)
    contact = factory.SubFactory(PersonFactory)

    class Meta:
        model = Device
