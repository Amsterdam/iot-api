import keycloak_oidc.auth
from django.conf import settings
from django.contrib.auth.models import Group
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse


def oidc_login(request, **kwargs):
    oidc_authentication_init = reverse('oidc_authentication_init')
    redirect = f'{oidc_authentication_init}?next={request.GET.get("next", "")}'
    return HttpResponseRedirect(redirect)


class OIDCAuthenticationBackend(keycloak_oidc.auth.OIDCAuthenticationBackend):
    def update_groups(self, user, claims):
        """
        Transform roles obtained from keycloak into Django Groups and
        add them to the user. Note that any role not passed via keycloak
        will be removed from the user.
        """
        with transaction.atomic():
            user.groups.clear()
            user.is_superuser = False
            user.save()
            for role in claims.get('roles'):
                group, _ = Group.objects.get_or_create(name=role)
                if settings.DEBUG or role == settings.SENSOR_REGISTER_ADMIN_ROLE_NAME:
                    user.is_staff = True
                    user.is_superuser = True
                user.save()
                group.user_set.add(user)
