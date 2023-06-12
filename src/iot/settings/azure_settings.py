import os
import shlex
import subprocess
from subprocess import PIPE

from azure.identity import DefaultAzureCredential, WorkloadIdentityCredential
from azure.keyvault.secrets import SecretClient


class SettingNotFound(Exception):
    pass


class AzureKeyVault:
    def __init__(self, auth, vault_url):
        self.auth = auth
        self.vault_url = vault_url
        self._secrets = {}

    @property
    def secrets(self):
        if not self._secrets and self.vault_url:
            self._secrets = self.get_secrets()

        return self._secrets

    def get_secrets(self):
        client = SecretClient(self.vault_url, self.auth.credential)
        secrets = [x for x in client.list_properties_of_secrets() if x.name]

        wanted = {}
        for properties in secrets:
            if not properties.enabled:
                continue
            if properties.managed:
                continue
            if not properties.name:
                continue
            secret = client.get_secret(properties.name)
            wanted[properties.name.replace('-', '_').upper()] = secret.value

        return wanted

    def get(self, name, default=None, use_environ=True, use_default=True):
        if use_environ and name in os.environ:
            return os.environ[name]

        if name in self.secrets:
            return self.secrets[name]

        if use_default:
            return default

        raise SettingNotFound(
            f"Setting '{name}' was not found and no default was specified"
        )

    def __getitem__(self, name):
        return self.get(name, use_default=False)


class AzureAuth:
    def __init__(self):
        self._credential = None

    @property
    def credential(self):
        if not self._credential:
            self._credential = self.get_credential()

        return self._credential

    def get_credential(self):
        credential = None
        federated_token_file = os.getenv('AZURE_FEDERATED_TOKEN_FILE')
        if federated_token_file:
            # This relies on environment variables that get injected.
            # AZURE_AUTHORITY_HOST:       (Injected by the webhook)
            # AZURE_CLIENT_ID:            (Injected by the webhook)
            # AZURE_TENANT_ID:            (Injected by the webhook)
            # AZURE_FEDERATED_TOKEN_FILE: (Injected by the webhook)
            credential = WorkloadIdentityCredential()
        elif os.isatty(0):
            account = subprocess.run(
                shlex.split('az account show'),
                check=False,
                stdout=PIPE,
                stderr=PIPE,
            )
            if account.returncode != 0:
                subprocess.run(
                    shlex.split('az login'),
                    check=True,
                    stdout=PIPE,
                )

            credential = DefaultAzureCredential(managed_identity_client_id=None)
        else:
            raise Exception('cannot connect to azure')

        return credential

    @property
    def db_password(self) -> object:
        # return access_token.token
        class DynamicString:
            def __init__(self, credential, scopes) -> None:
                self.credential = credential
                self.scopes = scopes

            def __str__(self):
                access_token = self.credential.get_token(*self.scopes)
                return access_token.token

        scopes = ['https://ossrdbms-aad.database.windows.net/.default']
        return DynamicString(self.credential, scopes)


class Azure:
    def __init__(self, key_vault_url=None) -> None:
        self.auth = AzureAuth()
        self.settings = AzureKeyVault(self.auth, key_vault_url)
