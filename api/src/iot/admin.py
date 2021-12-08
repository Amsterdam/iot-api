from django import forms
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.safestring import mark_safe
from leaflet.admin import LeafletGeoAdminMixin
from openpyxl import load_workbook
from simple_history.admin import SimpleHistoryAdmin

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


@staff_member_required
def import_xlsx_view(request, message_user, redirect_to):

    if request.method == "POST":
        try:
            file = request.FILES["selecteer_bestand"]
            workbook = load_workbook(file)
            errors, created, updated = import_xlsx(workbook)
            if created:
                message_user(request, f"{len(created)} sensoren aangemaakt")
            if updated:
                message_user(request, f"{len(updated)} sensoren bijgewerkt")
        except Exception as e:
            errors = [e]

        for e in errors:
            message_user(request, mark_safe(str(e)), level=messages.ERROR)

        return redirect(redirect_to)
    else:
        return render(request, "import_xlsx.html", {"form": FileForm()})


@admin.register(models.Device2)
class DeviceAdmin(LeafletGeoAdminMixin, SimpleHistoryAdmin):

    change_list_template = "devices_change_list.html"
    list_display = 'reference', 'owner', 'type'
    filter_horizontal = 'themes',
    settings_overrides = LEAFLET_SETTINGS_OVERRIDES
    search_fields = 'reference', 'owner__organisation', 'owner__email', 'owner__name'

    def get_urls(self):
        _meta = self.model._meta
        context = dict(
            message_user=self.message_user,
            redirect_to=f"admin:{_meta.app_label}_{_meta.model_name}_changelist",
        )
        import_xlsx_path = path('import_xlsx/', import_xlsx_view, context)
        return [import_xlsx_path] + super().get_urls()


class DeviceInline(LeafletGeoAdminMixin, admin.StackedInline):
    model = models.Device2
    extra = 0
    settings_overrides = LEAFLET_SETTINGS_OVERRIDES


@admin.register(models.Person2)
class PersonAdmin(LeafletGeoAdminMixin, SimpleHistoryAdmin):
    search_fields = 'organisation', 'email', 'name'
    inlines = [DeviceInline]
