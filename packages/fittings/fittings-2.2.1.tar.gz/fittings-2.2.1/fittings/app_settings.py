from django.apps import apps
from django.conf import settings

FITTINGS_AADISCORDBOT_INTEGRATION = getattr(settings, 'FITTINGS_AADISCORDBOT_INTEGRATION', True)

def is_installed(app_name: str) -> bool:
    """
    Check if a Django app is installed.

    :param app_name:
    :type app_name:
    :return:
    :rtype:
    """

    return apps.is_installed(app_name)
