from datapunt_api.rest import HALSerializer

from .models import Address, Device, Type


class AddressSerializer(HALSerializer):
    class Meta:
        model = Address
        fields = (
            'street',
            'postal_code',
            'city',
        )


class TypeSerializer(HALSerializer):
    class Meta:
        model = Type
        fields = (
            'name',
            'application',
            'description',
        )


class DeviceSerializer(HALSerializer):
    address = AddressSerializer()
    type = TypeSerializer()

    class Meta:
        model = Device
        fields = (
            '_links',
            'reference',
            'application',
            'type',
            'installation_point',
            'longitude',
            'latitude',
            'address',
            'organisation',
        )
