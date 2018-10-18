from datapunt_api.rest import HALSerializer

from .models import Address, Device, Owner, Type


class AddressSerializer(HALSerializer):
    class Meta:
        model = Address
        fields = (
            'street',
            'postal_code',
            'city',
            'municipality',
            'country',
        )


class OwnerSerializer(HALSerializer):
    class Meta:
        model = Owner
        fields = (
            'name',
            'email',
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
    owner = OwnerSerializer()
    type = TypeSerializer()

    class Meta:
        model = Device
        fields = (
            '_links',
            'reference',
            'application',
            'longitude',
            'latitude',
            'owner',
            'address',
            'type',
        )
