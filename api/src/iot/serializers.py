from datapunt_api.rest import HALSerializer
from drf_extra_fields.geo_fields import PointField
from rest_framework import serializers

from iot.constants import CATEGORY_CHOICE_ABBREVIATIONS, CATEGORY_CHOICES
from iot.tasks import send_iot_request

from .models import Device, Person, Type


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
    organisation = serializers.CharField(required=False, allow_blank=True, max_length=250)

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
    owner = PersonSerializer(required=False)
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
            'contact'
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
                    f'categories needs to be either of {",".join(CATEGORY_CHOICE_ABBREVIATIONS)}')
        return categories

    def create(self, validated_data):
        types_data = validated_data.pop('types')
        owner_data = validated_data.pop('owner', None)
        contact_data = validated_data.pop('contact', None)

        device = Device.objects.create(**validated_data)

        # Serialize Types
        for type_data in types_data:
            t, _ = Type.objects.get_or_create(**type_data)
            device.types.add(t)

        # Serialize Owner and Contact
        if owner_data:
            owner, _ = Person.objects.get_or_create(**owner_data)
            device.owner = owner
        if contact_data:
            contact, created = Person.objects.get_or_create(**contact_data)
            device.contact = contact

        device.save()
        return device


class IotContactSerializer(serializers.Serializer):
    device = serializers.CharField(
        required=True,
    )

    name = serializers.CharField(
        required=True,
    )

    email = serializers.EmailField(
        required=True,
    )

    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=250,
    )

    can_i_have_access = serializers.BooleanField(
        default=False,
    )

    can_i_get_more_information = serializers.BooleanField(
        default=False,
    )

    can_i_use_collected_data = serializers.BooleanField(
        default=False,
    )

    does_the_device_register_personal_data = serializers.BooleanField(
        default=False,
    )

    def validate_device(self, value):
        try:
            device = Device.objects.get(pk=value)
            return device.pk
        except Device.DoesNotExist:
            raise serializers.ValidationError('Device does not exists')

    def save(self, **kwargs):
        # We do not actualy store any data
        device = self.validated_data['device']
        send_iot_request(device_id=device, form_data=self.validated_data)
