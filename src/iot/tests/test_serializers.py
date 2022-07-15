import pytest

from iot import factories, models, serializers


@pytest.mark.django_db
class TestIsOtherEntitySerializer:

    def test_theme_is_other_values_should_be_grouped_under_overig(self):
        instance = factories.Device2Factory()
        instance.themes.all().delete()
        themes = [models.Theme(name=str(i), is_other=True) for i in range(2)]
        for theme in models.Theme.objects.bulk_create(themes):
            instance.themes.add(theme)
        assert serializers.Device2Serializer(instance).data['themes'] == ['Overig']

    def test_theme_standard_values_should_not_be_grouped_under_overig(self):
        instance = factories.Device2Factory()
        instance.themes.all().delete()
        themes = [models.Theme(name=str(i), is_other=False) for i in range(2)]
        for theme in models.Theme.objects.bulk_create(themes):
            instance.themes.add(theme)
        assert serializers.Device2Serializer(instance).data['themes'] == ['0', '1']

    def test_type_is_other_values_should_be_grouped_under_overig(self):
        instance = factories.Device2Factory()
        instance.type = models.Type2(name='something', is_other=True)
        instance.type.save()
        assert serializers.Device2Serializer(instance).data['type'] == 'Overig'

    def test_type_standard_values_should_be_not_grouped_under_overig(self):
        instance = factories.Device2Factory()
        instance.type = models.Type2(name='something', is_other=False)
        instance.type.save()
        assert serializers.Device2Serializer(instance).data['type'] == 'something'
