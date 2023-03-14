from datapunt_api.rest import HALSerializer
from rest_framework import serializers
from rest_framework.fields import DateField, JSONField
from rest_framework.serializers import Serializer

from .models import Device, ObservationGoal, Person, Project


class PersonSerializer(HALSerializer):
    class Meta:
        model = Person
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


class DeviceSerializer(HALSerializer):
    type = serializers.SerializerMethodField()
    regions = serializers.StringRelatedField(many=True)
    themes = serializers.SerializerMethodField()
    owner = PersonSerializer()
    location = serializers.SerializerMethodField()
    observation_goals = ObservationGoalSerializer(many=True)
    project_paths = ProjectSerializer(many=True, source='projects')

    class Meta:
        model = Device
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
        return list(
            filter(lambda x: x is not None, super().to_representation(instance))
        )


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
