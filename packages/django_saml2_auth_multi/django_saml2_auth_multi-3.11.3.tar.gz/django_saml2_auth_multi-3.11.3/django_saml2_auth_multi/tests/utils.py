import pytest_django.fixtures

from django_saml2_auth_multi.config import SAML2_SETTINGS


class SettingsWrapper(pytest_django.fixtures.SettingsWrapper):

    def finalize(self) -> None:
        super().finalize()
        SAML2_SETTINGS.load()
