
from django.conf import settings


def get_kubi_feature(feature_name):
    kubi_settings = getattr(settings, 'DJANGO_ADMIN_KUBI', {})
    return kubi_settings.get(feature_name, False)


def is_setup_flow_enabled():
    return 'django_admin_kubi.middleware.SetupMiddleware' in settings.MIDDLEWARE
