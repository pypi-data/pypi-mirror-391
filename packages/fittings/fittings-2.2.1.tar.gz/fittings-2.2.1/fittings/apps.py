from django.apps import AppConfig
from . import __version__


class FittingsConfig(AppConfig):
    name = 'fittings'
    verbose_name = f"Fittings v{__version__}"
