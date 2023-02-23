import os
import shlex
import subprocess
from subprocess import PIPE

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
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
        secrets = [x.name for x in client.list_properties_of_secrets() if x.name]

        wanted = {}
        for name in secrets:
            secret = client.get_secret(name)
            if not secret.properties.enabled:
                continue
            if secret.properties.managed:
                continue
            if not secret.name:
                continue
            wanted[secret.name.replace('-', '_').upper()] = secret.value

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
        client_id = os.getenv('MANAGED_IDENTITY_CLIENTID')
        if client_id:
            credential = ManagedIdentityCredential(client_id=client_id)
        else:
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

        return credential

    @property
    def db_password(self) -> str:
        SCOPES = ['https://ossrdbms-aad.database.windows.net']
        access_token = self.credential.get_token(*SCOPES)
        return access_token.token


class Azure:
    def __init__(self, key_vault_url=None) -> None:
        self.auth = AzureAuth()
        self.settings = AzureKeyVault(self.auth, key_vault_url)
