import random

import factory
import faker
from django.contrib.gis.geos import Point

from iot.models import Device, ObservationGoal, Person, Project, Theme, Type

fake = faker.Faker()


class PersonFactory(factory.django.DjangoModelFactory):
    name = fake.name()
    email = fake.company_email()
    telephone = '06123456789'
    organisation = fake.company()
    website = fake.url(['https'])

    class Meta:
        model = Person


def sample_model(model, n=1):
    population = list(model.objects.all())
    assert n <= len(population)
    return random.sample(population, n)


class DeviceFactory(factory.django.DjangoModelFactory):
    reference = fake.text(64)
    owner = factory.SubFactory(PersonFactory)
    type = factory.LazyFunction(lambda: sample_model(Type)[0])
    location = Point(4.58565, 52.03560)
    datastream = fake.text(255)

    @factory.post_generation
    def themes(self, *args, **kwargs):
        for theme in sample_model(Theme, random.randint(1, 3)):
            self.themes.add(theme)

    contains_pi_data = fake.boolean()

    @factory.post_generation
    def observation_goals(self, *args, **kwargs):
        for observation_goal, privacy_declaration, legal_ground in sample_model(
            ObservationGoal, 0
        ):
            self.observation_goal.add(
                observation_goal, privacy_declaration, legal_ground
            )

    @factory.post_generation
    def projects(self, *args, **kwargs):
        for path in sample_model(Project, 0):
            self.projects.add(path)

    active_until = fake.date()

    class Meta:
        model = Device
