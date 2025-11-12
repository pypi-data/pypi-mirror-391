import pytest
from pytest_django.fixtures import SettingsWrapper
from pytest_django.lazy_django import skip_if_no_django

from django_saml2_auth_multi.config import SAML2_SETTINGS


@pytest.fixture()
def settings():
    """A Django settings object which restores changes after the testrun"""
    skip_if_no_django()

    wrapper = SettingsWrapper()
    yield wrapper
    wrapper.finalize()
    SAML2_SETTINGS.load()
