from django import forms
from django.contrib import admin, messages
from django.contrib.admin.models import ADDITION, CHANGE, LogEntry
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from leaflet.admin import LeafletGeoAdmin, LeafletGeoAdminMixin
from openpyxl import load_workbook

from iot import models
from iot.importers.import_xlsx import import_xlsx

admin.site.register(models.Type)
admin.site.register(models.Theme)
admin.site.register(models.LegalGround)
admin.site.register(models.ObservationGoal)
admin.site.register(models.Project)


LEAFLET_SETTINGS_OVERRIDES = {
    'DEFAULT_CENTER': (52.3676, 4.9041),
    'DEFAULT_ZOOM': 11,
}


class FileForm(forms.Form):
    selecteer_bestand = forms.FileField()


@staff_member_required
def import_xlsx_view(request, message_user, redirect_to):
    if request.method == "POST":
        file = request.FILES["selecteer_bestand"]
        num_created = 0
        num_updated = 0
        imported_sensors = []
        try:
            workbook = load_workbook(file)

            def action_logger(result):
                instance, created = result
                action = 'Aangemaakt' if created else 'Bijgewerkt'
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    object_id=instance.pk,
                    object_repr=str(instance),
                    content_type_id=ContentType.objects.get_for_model(
                        type(instance)
                    ).pk,
                    action_flag=ADDITION if created else CHANGE,
                    change_message=f'{action} door het importeren van "{file.name}"',
                )
                return result

            (
                errors,
                imported_sensors,
                num_created,
                num_updated,
            ) = import_xlsx(workbook, action_logger)

        except Exception as e:
            errors = [e]

        send_messages_to_user(request, message_user, num_created, num_updated, errors)

        # warn about any sensors that do not have a lat/long, these sensors
        # will be imported in the registry, however it won't be possible to
        # show them on the map
        def change_url(s):
            return reverse(
                f'admin:{s._meta.app_label}_{s._meta.model_name}_change', args=(s.pk,)
            )

        sensors_with_no_location = [
            f'<a target="_blank" href="{change_url(s)}">{s.reference}</a>'
            for s in imported_sensors
            if s.location is None
        ]

        if sensors_with_no_location:
            message = (
                "De volgende sensoren hebben geen lat/long, en "
                "kunnen dus niet op de kaart getoond worden: <br>"
            )
            message += '<br>'.join(sensors_with_no_location)
            message_user(request, mark_safe(message), messages.WARNING)

        return redirect(redirect_to)
    else:
        return render(request, "import_xlsx.html", {"form": FileForm()})


def send_messages_to_user(request, message_user, num_created, num_updated, errors):
    """
    Give the user feedback about what was imported, and any errors that
    occurred.
    """
    message = f"{num_created} sensoren aangemaakt<br>{num_updated} sensoren bijgewerkt"

    if errors:
        level = messages.WARNING if num_created and not num_updated else messages.ERROR
        plural = 'en' if len(errors) > 1 else ''
        message += f"<br>{len(errors)} fout{plural} gevonden:"
    else:
        level = messages.INFO

    message_user(request, mark_safe(message), level)

    if errors:
        max_num_errors_to_show = 10
        show, hide = errors[:max_num_errors_to_show], errors[max_num_errors_to_show:]
        for e in show:
            message_user(request, mark_safe(str(e)), level=messages.ERROR)

        if hide:
            plural = 'en' if len(hide) > 1 else ''
            message_user(
                request, f'+ nog {len(hide)} fout{plural}', level=messages.ERROR
            )


@admin.register(models.Device)
class DeviceAdmin(LeafletGeoAdmin):
    change_list_template = "devices_change_list.html"
    list_display = (
        'reference',
        'owner',
        'type',
        'location',
    )
    filter_horizontal = ('themes',)
    settings_overrides = LEAFLET_SETTINGS_OVERRIDES
    search_fields = 'reference', 'owner__organisation', 'owner__email', 'owner__name'
    list_filter = (('location', admin.EmptyFieldListFilter),)

    def get_urls(self):
        _meta = self.model._meta
        context = dict(
            message_user=self.message_user,
            redirect_to=f"admin:{_meta.app_label}_{_meta.model_name}_changelist",
        )
        import_xlsx_path = path('import_xlsx/', import_xlsx_view, context)
        return [import_xlsx_path] + super().get_urls()


class DeviceInline(LeafletGeoAdminMixin, admin.StackedInline):
    model = models.Device
    extra = 1
    settings_overrides = LEAFLET_SETTINGS_OVERRIDES


@admin.register(models.Person)
class PersonAdmin(LeafletGeoAdmin):
    search_fields = 'organisation', 'email', 'name'
    inlines = [DeviceInline]


class ObservationGoalAdmin(LeafletGeoAdmin):
    list_display = 'observation_goal', 'privacy_declaration', 'legal_ground'
    search_fields = 'observation_goal', 'privacy_declaration', 'legal_ground'
    model = models.ObservationGoal


class ProjectAdmin(LeafletGeoAdmin):
    list_display = 'path'
    search_fields = 'path'
    model = models.Project
