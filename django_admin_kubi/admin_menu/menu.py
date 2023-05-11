from __future__ import unicode_literals

from fnmatch import fnmatch
from collections import OrderedDict

from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_admin_kubi.admin_menu.items import *
import six

# by default exclude all auth models
DEFAULT_EXCLUDE_MODELS = ("django.contrib.auth.*", )


class MenuBase(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(MenuBase, cls).__new__

        # Also ensure initialization is only performed for subclasses of Menu
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, MenuBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        current_items = []
        for key, value in list(attrs.items()):
            if isinstance(value, MenuItem):
                current_items.append((key, value))
                attrs.pop(key)
        current_items.sort(key=lambda x: x[1].creation_counter)

        attrs['declared_items'] = OrderedDict(current_items)

        new_class = super_new(cls, name, bases, attrs)

        return new_class


class Menu(six.with_metaclass(MenuBase)):
    children = None
    context = None
    available_models = None

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self.__class__, key):
                setattr(self, key, kwargs[key])
        self.children = kwargs.get('children', [])

        for key, item in self.declared_items.items():
            item.set_parent(self)

    def __iter__(self):
        for key, item in self.declared_items.items():
            yield item

    def get_admin_site(self):
        return admin.site

    def get_admin_site_name(self):
        return self.get_admin_site().name

    def get_avail_models(self, request):
        """ Returns (model, perm,) for all models user can possibly see """
        items = []
        admin_site = admin.site

        for model, model_admin in admin_site._registry.items():
            perms = model_admin.get_model_perms(request)
            if True not in perms.values():
                continue
            items.append((model, perms,))
        return items

    def get_model(self, pattern):
        items = self.available_models
        full_name = lambda model: '%s.%s' % (model.__module__, model.__name__)

        for item in items:
            model, perms = item
            if full_name(model) == pattern:
                return item

        return None

    def filter_models(self, models, exclude):
        """
        Returns (model, perm,) for all models that match models/exclude patterns
        and are visible by current user.
        """
        items = self.available_models
        included = []
        full_name = lambda model: '%s.%s' % (model.__module__, model.__name__)

        if len(models) == 0:
            included = items
        else:
            for pattern in models:
                for item in items:
                    model, perms = item
                    if fnmatch(full_name(model), pattern) and item not in included:
                        included.append(item)

        result = included[:]
        for pattern in exclude:
            for item in included:
                model, perms = item
                if fnmatch(full_name(model), pattern):
                    result.remove(item)
        return result

    def set_context(self, context):
        self.context = context
        request = context.get('request')
        if not request:
            raise ImproperlyConfigured("Missing Request Processor")
        self.available_models = self.get_avail_models(request)

    def _get_admin_app_list_url(self, model):
        """
        Returns the admin change url.
        """
        app_label = model._meta.app_label
        return reverse('%s:app_list' % self.get_admin_site_name(), args=(app_label,))

    def _get_admin_change_url(self, model):
        """
        Returns the admin change url.
        """
        app_label = model._meta.app_label
        return reverse('%s:%s_%s_changelist' % (self.get_admin_site_name(),
                                                app_label,
                                                model.__name__.lower()))

    def _get_admin_add_url(self, model):
        """
        Returns the admin add url.
        """
        app_label = model._meta.app_label
        return reverse('%s:%s_%s_add' % (self.get_admin_site_name(),
                                         app_label,
                                         model.__name__.lower()))


class AdminMenu(Menu):
    dashboard = MenuItem(_('Dashboard'), reverse('admin:index'), icon="fa-th-large")
    applications = AppList(_('Applications'), models=("*"), exclude=DEFAULT_EXCLUDE_MODELS, icon="fa-laptop")
    administration = ModelList(_('Administration'), models=DEFAULT_EXCLUDE_MODELS, icon="fa-cogs")
