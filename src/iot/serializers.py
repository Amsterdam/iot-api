from datapunt_api.rest import HALSerializer
from drf_extra_fields.geo_fields import PointField
from rest_framework import serializers
from rest_framework.fields import DateField, JSONField
from rest_framework.serializers import Serializer

from .constants import CATEGORY_CHOICE_ABBREVIATIONS, CATEGORY_CHOICES
from .models import Device, Device2, ObservationGoal, Person, Person2, Project, Type


class TypeSerializer(HALSerializer):
    class Meta:
        model = Type
        fields = ('name', 'application', 'description')


class ChoicesField(serializers.CharField):
    def __init__(self, choices, **kwargs):
        self._choices = choices
        super(ChoicesField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        if value is None or value == "":
            return []
        return [dict(self._choices)[key.upper()] for key in value.split(",")]


class PersonSerializer(HALSerializer):
    name = serializers.CharField(required=True, allow_blank=False, max_length=255)
    email = serializers.EmailField()
    organisation = serializers.CharField(
        required=False, allow_blank=True, max_length=250
    )

    class Meta:
        model = Person
        fields = ('name', 'email', 'organisation')


class DeviceSerializer(HALSerializer):
    types = TypeSerializer(many=True)
    categories = ChoicesField(CATEGORY_CHOICES, required=True, allow_blank=False)
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    geometrie = PointField(required=False)
    organisation = serializers.SerializerMethodField()
    owner = PersonSerializer()
    contact = PersonSerializer(required=False)

    class Meta:
        model = Device
        fields = (
            '_links',
            'id',
            'reference',
            'application',
            'types',
            'categories',
            'installation_point',
            'frequency',
            'permit',
            'in_use_since',
            'postal_code',
            'house_number',
            'longitude',
            'latitude',
            'geometrie',
            'organisation',
            'owner',
            'contact',
        )

    def get_organisation(self, obj):
        if obj.owner:
            return obj.owner.organisation
        return 'Onbekend'

    def get_longitude(self, obj):
        if obj.geometrie:
            return obj.geometrie.x

    def get_latitude(self, obj):
        if obj.geometrie:
            return obj.geometrie.y

    def validate_categories(self, categories):
        for category in categories.split(","):
            if category not in CATEGORY_CHOICE_ABBREVIATIONS:
                raise serializers.ValidationError(
                    f'categories needs to be either of {",".join(CATEGORY_CHOICE_ABBREVIATIONS)}'
                )
        return categories

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Only serve the owner and contact if the logged in user is the owner of the data.
        # Note that the organisation is served anyway by get_organisation() above.
        if (
            not self.context['request'].user
            or instance.owner.email != self.context['request'].user.email
        ):
            data.pop('owner')
            data.pop('contact')

        return data

    def create(self, validated_data):
        types_data = validated_data.pop('types')
        owner_data = validated_data.pop('owner', None)
        contact_data = validated_data.pop('contact', None)

        device = Device.objects.create(**validated_data)

        # Serialize Types
        for type_data in types_data:
            t, _ = Type.objects.get_or_create(**type_data)
            device.types.add(t)

        # Serialize Owner
        user = self.context['request'].user
        device.owner = Person.objects.filter(email__iexact=user.email).first()
        if not device.owner:
            # We always take the name and email address of the keycloak credentials,
            # so we just use the organisation from the supplied owner object
            owner = Person.objects.create(
                name=f"{user.first_name} {user.last_name}",
                email=user.email.lower(),
                organisation=owner_data.get('organisation', None),
            )
            device.owner = owner

        # Serialize Contact
        if contact_data:
            if not contact_data.get('organisation', None):
                contact_data['organisation'] = owner_data.get('organisation', None)
            device.contact, created = Person.objects.get_or_create(**contact_data)
        else:
            device.contact = device.owner

        device.save()
        return device


class Person2Serializer(HALSerializer):
    class Meta:
        model = Person2
        fields = ['name', 'email', 'organisation']


class ObservationGoalSerializer(HALSerializer):

    legal_ground = serializers.StringRelatedField()

    class Meta:
        model = ObservationGoal
        fields = ['observation_goal', 'privacy_declaration', 'legal_ground']


class ProjectSerializer(HALSerializer):

    # converts the string list to a list.
    path = serializers.ListField(child=serializers.StringRelatedField())

    class Meta:
        model = Project
        fields = ['path']

    def to_representation(self, instance):
        """print only the list values without the whole object of Project"""
        representation = super().to_representation(instance)
        return representation['path']


class Device2Serializer(HALSerializer):
    type = serializers.SerializerMethodField()
    regions = serializers.StringRelatedField(many=True)
    themes = serializers.SerializerMethodField()
    owner = Person2Serializer()
    location = serializers.SerializerMethodField()
    observation_goals = ObservationGoalSerializer(many=True)
    project_paths = ProjectSerializer(many=True, source='projects')

    class Meta:
        model = Device2
        fields = [
            'owner',
            'type',
            'regions',
            'location',
            'location_description',
            'datastream',
            'themes',
            'contains_pi_data',
            'observation_goals',
            'project_paths',
            'active_until',
            'reference',
        ]

    def get_location(self, obj):
        if obj.location:
            return {'latitude': obj.location.y, 'longitude': obj.location.x}

    def get_themes(self, obj):
        themes = (
            'Overig' if theme.is_other else theme.name for theme in obj.themes.all()
        )
        return list(
            dict.fromkeys(themes)
        )  # use a dict.fromkeys to preserve original order

    def get_type(self, obj):
        return 'Overig' if obj.type.is_other else obj.type.name


class JSONFieldFilterNone(JSONField):
    def to_representation(self, instance):
        # it should be possible to filter out None values from the
        # array in SQL (https://modern-sql.com/feature/filter) but I
        # can't seem to get it working with django, so we filter them
        # out here instead.
        return list(filter(lambda x: x is not None, super().to_representation(instance)))


class DeviceJsonSerializer(Serializer):
    active_until = DateField()
    contains_pi_data = JSONField()
    datastream = JSONField()
    location_description = JSONField()
    reference = JSONField()
    type = JSONField(source="type__name")
    themes = JSONField(source='_themes')
    owner = JSONField(source='_owner')
    location = JSONField(source='_location')
    observation_goals = JSONFieldFilterNone(source='_observation_goals')
    project_paths = JSONFieldFilterNone(source='_project_paths')
    regions = JSONFieldFilterNone(source='_regions')
