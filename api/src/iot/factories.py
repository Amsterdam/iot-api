import random

import factory
import faker

from .models import Address, Device, Owner, Type

fake = faker.Faker()


class AddressFactory(factory.DjangoModelFactory):
    class Meta:
        model = Address

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


class OwnerFactory(factory.DjangoModelFactory):

    class Meta:
        model = Owner

    name = factory.LazyAttribute(
        lambda o: '{0}'.format(fake.user_name())
    )

    email = factory.LazyAttribute(
        lambda o: '{0}@amsterdam.nl'.format(o.name)
    )


class TypeFactory(factory.DjangoModelFactory):

    class Meta:
        model = Type

    name = factory.LazyAttribute(
        lambda o: '{0}'.format(fake.text(max_nb_chars=32))
    )

    application = factory.LazyAttribute(
        lambda o: fake.text(max_nb_chars=32)
    )

    description = factory.LazyAttribute(
        lambda o: fake.text(max_nb_chars=128)
    )


class DeviceFactory(factory.DjangoModelFactory):

    class Meta:
        model = Device

    reference = factory.LazyAttribute(
        lambda o: fake.text(max_nb_chars=32)
    )

    application = factory.LazyAttribute(
        lambda o: fake.text(max_nb_chars=32)
    )

    longitude = factory.LazyAttribute(
        lambda o: fake.longitude()
    )

    latitude = factory.LazyAttribute(
        lambda o: fake.latitude()
    )

    owner = factory.SubFactory(OwnerFactory)

    address = factory.SubFactory(AddressFactory)

    type = factory.SubFactory(TypeFactory)
