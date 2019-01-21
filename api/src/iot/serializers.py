from datapunt_api.rest import HALSerializer
from rest_framework import serializers

from iot.tasks import send_iot_request

from .models import Device, Type


class TypeSerializer(HALSerializer):
    class Meta:
        model = Type
        fields = (
            'name',
            'application',
            'description',
        )


class DeviceSerializer(HALSerializer):
    types = TypeSerializer(many=True)
    categories = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    organisation = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = (
            '_links',
            'id',
            'reference',
            'application',
            'types',
            'categories',
            'longitude',
            'latitude',
            'organisation',
        )

    def get_categories(self, obj):
        return [
            obj.categories.choices[key.upper()]
            for key in obj.categories

        ]

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
