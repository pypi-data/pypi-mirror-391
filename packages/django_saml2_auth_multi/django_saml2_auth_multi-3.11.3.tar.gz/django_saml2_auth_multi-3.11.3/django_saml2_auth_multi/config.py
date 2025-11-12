import logging
from copy import deepcopy

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class SAMLSettings:

    def __init__(self):
        self.debug = False
        self.logger = None
        self.defaults = {}
        self._idp_settings = {}
        self.load()

    def load(self):
        if not hasattr(settings, "SAML2_AUTH"):
            raise ImproperlyConfigured(
                "'AUTH_SAML2' settings variable is not found in the Django settings"
            )
        saml2_settings = settings.SAML2_AUTH

        self.debug = getattr(settings, "SAML2_AUTH_DEBUG", False)
        self.logger = getattr(settings, "SAML2_AUTH_LOGGER", None)
        self.defaults = getattr(settings, "SAML2_AUTH_DEFAULTS", {})
        self._idp_settings = self.load_idp_settings(saml2_settings, self.defaults)

    def load_idp_settings(self, idp_config, defaults):
        idp = {}
        if isinstance(idp_config, list):
            for conf in idp_config:
                if "IDP_ID" not in conf:
                    raise ImproperlyConfigured(
                        "Entity ID ('ID') of an IDP config is not set in 'SAML2_AUTH'. "
                        "Set it to Entity ID of your IDP"
                    )
                idp_id = conf["IDP_ID"]
                base = deepcopy(defaults)
                base.update(conf)
                idp[idp_id] = base
        else:
            base = deepcopy(defaults)
            base.update(idp_config)
            idp["__default__"] = base
        return idp

    def get_idp_settings(self, name):
        if name is None:
            return self.default()
        return self._idp_settings[name]

    def default(self):
        return self._idp_settings["__default__"]

    def get_logger(self, name: str | None = None):
        return self.logger or logging.getLogger(name)


SAML2_SETTINGS = SAMLSettings()
