from functools import partial

from django import forms
from django.contrib import admin, messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.safestring import mark_safe
from leaflet.admin import LeafletGeoAdmin, LeafletGeoAdminMixin
from openpyxl import load_workbook

from iot import models
from iot.import_utils import import_xlsx

admin.site.register(models.Type2)
admin.site.register(models.Theme)
admin.site.register(models.LegalGround)


LEAFLET_SETTINGS_OVERRIDES = {
    'DEFAULT_CENTER': (52.3676, 4.9041),
    'DEFAULT_ZOOM': 11,
}


class FileForm(forms.Form):
    selecteer_bestand = forms.FileField()


@login_required
def import_xlsx_view(request, message_user):
    if request.method == "POST":
        try:
            file = request.FILES["selecteer_bestand"]
            workbook = load_workbook(file)
            errors, created, updated = import_xlsx(workbook)
            if errors:
                for e in errors:
                    message_user(request, mark_safe(str(e)), level=messages.ERROR)
            else:
                # TODO: information about what was imported
                for sensor in created:
                    message_user(request, f"Sensor met referentie {sensor.reference} aangemaakt")
                for sensor in updated:
                    message_user(request, f"Sensor met referentie {sensor.reference} bijgewerkt")
        except Exception as e:
            message_user(request, mark_safe(str(e)), level=messages.ERROR)
        return redirect("..")

    return render(request, "import_xlsx.html", {"form": FileForm()})


@admin.register(models.Device2)
class DeviceAdmin(LeafletGeoAdmin):

    change_list_template = "devices_change_list.html"
    list_display = 'reference', 'owner', 'type'
    filter_horizontal = 'themes',
    settings_overrides = LEAFLET_SETTINGS_OVERRIDES
    search_fields = 'reference', 'owner__organisation', 'owner__email', 'owner__name'

    def get_urls(self):
        import_xlsx_path = path(
            'import_xlsx/',
            partial(import_xlsx, message_user=self.message_user),
        )
        return [import_xlsx_path] + super().get_urls()


class DeviceInline(LeafletGeoAdminMixin, admin.StackedInline):
    model = models.Device2
    extra = 1
    settings_overrides = LEAFLET_SETTINGS_OVERRIDES


@admin.register(models.Person2)
class PersonAdmin(LeafletGeoAdmin):
    search_fields = 'organisation', 'email', 'name'
    inlines = [DeviceInline]
