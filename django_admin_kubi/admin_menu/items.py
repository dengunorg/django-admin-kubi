from functools import total_ordering

from django.conf import settings
from django.utils.text import capfirst
from django.template.loader import render_to_string


def get_model_icon_overwrites(model):
    MODEL_NAME_ICON_MAP = {
        "User": "fa-user",
        "Group": "fa-users",
        "Tag": "fa-tags",
        "Site": "fa-globe",
        "LogEntry": "fa-clipboard-list",
        "Watermark": "fa-marker",
        "PhotoEffect": "fa-spray-can",
        "PhotoSize": "fa-crop-alt",
        "Photo": "fa-image",
        "Gallery": "fa-images",

    }
    model_name = model.__name__
    if hasattr(settings, "MODEL_NAME_ICON_MAP"):
        MODEL_NAME_ICON_MAP = settings.MODEL_NAME_ICON_MAP
    return MODEL_NAME_ICON_MAP.get(model_name, None)


@total_ordering
class MenuItem(object):
    menu = None
    title = 'Menu item'
    url = '#'
    css_classes = None
    enabled = True
    children = None
    icon = None
    parent = None
    creation_counter = 0

    def __eq__(self, other):
        # Needed for @total_ordering
        if isinstance(other, MenuItem):
            return self.creation_counter == other.creation_counter
        return NotImplemented

    def __lt__(self, other):
        # This is needed because bisect does not take a comparison function.
        if isinstance(other, MenuItem):
            return self.creation_counter < other.creation_counter
        return NotImplemented

    def __hash__(self):
        return hash(self.creation_counter)

    def __init__(self, title, url=None, **kwargs):
        self.title = title

        if url is not None:
            self.url = url

        self.children = self.children or []
        self.icon = kwargs.get('icon', None)

        self.creation_counter = MenuItem.creation_counter
        MenuItem.creation_counter += 1

        # limit creation_counter to 1000, menus should not be this big
        if MenuItem.creation_counter > 1000:
            MenuItem.creation_counter = 0

    def render(self):
        if not self.context():
            return ""
        if self.url == "#" and not self.children:
            return ""

        self.set_parent_to_children()

        context = {
            'icon': self.icon,
            'title': self.title,
            'url': self.url,
            'children': self.children,
            'is_selected': self.is_selected(),
            'parent': self.parent,
        }
        return render_to_string('admin/sidebar_item.html', context)

    def context(self):
        return True

    def set_parent(self, parent):
        if isinstance(parent, MenuItem):
            self.parent = parent
            self.menu = self.parent.menu
        else:
            self.parent = None
            self.menu = parent

    def set_parent_to_children(self):
        for child in self.children:
            child.set_parent(self)

    def is_selected(self, request=None):
        if not request and self.menu:
            request = self.menu.context.get("request")
        if request:
            current_url = request.get_full_path()
            return self.url == current_url or \
                len([c for c in self.children if c.is_selected(request)]) > 0

        return False


class ModelUrl(MenuItem):
    model = None

    def __init__(self, title, model, **kwargs):
        self.model = model
        super(ModelUrl, self).__init__(title, **kwargs)

    def context(self):
        item = self.menu.get_model(self.model)
        if item:
            model, perms = item
            if perms['view']:
                if hasattr(model, 'Menu'):
                    if hasattr(model.Menu, 'icon'):
                        self.icon = model.Menu.icon

                self.title = capfirst(model._meta.verbose_name_plural)
                self.url = self.menu._get_admin_change_url(model)

                return True

        return False


class ModelItem(MenuItem):
    model = None

    def __init__(self, model, title=None, **kwargs):
        self.model = model
        super(ModelItem, self).__init__(title, **kwargs)

    def context(self):
        item = self.menu.get_model(self.model)
        if item:
            model, perms = item
            if perms['view']:
                if hasattr(model, 'Menu'):
                    if hasattr(model.Menu, 'icon'):
                        self.icon = model.Menu.icon

                self.title = capfirst(model._meta.verbose_name_plural)
                self.url = self.menu._get_admin_change_url(model)

                return True

        return False


class AppList(MenuItem):
    def __init__(self, title=None, **kwargs):
        self.models = list(kwargs.pop('models', []))
        self.exclude = list(kwargs.pop('exclude', []))
        super(AppList, self).__init__(title, **kwargs)

    def context(self):
        self.children = []
        items = self.menu.filter_models(self.models[:], self.exclude[:])
        apps = {}
        for model, perms in items:
            if not perms['view']:
                continue

            icon = None
            title = capfirst(model._meta.verbose_name_plural)

            app_label = model._meta.app_config.verbose_name
            if app_label not in apps:
                apps[app_label] = {
                    'title': capfirst(app_label.title()),
                    'icon': icon,
                    'url': self.menu._get_admin_app_list_url(model),
                    'models': []
                }

            if hasattr(model, 'Menu'):
                if hasattr(model.Menu, 'title'):
                    title = model.Menu.title
                if hasattr(model.Menu, 'icon'):
                    icon = model.Menu.icon

            apps[app_label]['models'].append({
                'icon': icon,
                'title': title,
                'url': self.menu._get_admin_change_url(model)
            })

        # sort key names
        apps_sorted = list(apps.keys())
        apps_sorted.sort()

        for app in apps_sorted:
            app_dict = apps[app]
            item = MenuItem(title=app_dict['title'], url=app_dict['url'], icon=app_dict['icon'])

            for model_dict in apps[app]['models']:
                item.children.append(MenuItem(**model_dict))
            self.children.append(item)

        return True


class ModelList(MenuItem):
    def __init__(self, title, models, exclude=None, **kwargs):
        self.models = list(models or [])
        self.exclude = list(exclude or [])
        super(ModelList, self).__init__(title, **kwargs)

    def context(self):
        self.children = []
        items = self.menu.filter_models(self.models[:], self.exclude[:])

        for model, perms in items:
            if not perms['view']:
                continue

            title = capfirst(model._meta.verbose_name_plural)
            icon = get_model_icon_overwrites(model)
            if hasattr(model, 'Menu'):
                if hasattr(model.Menu, 'title'):
                    title = model.Menu.title
                if hasattr(model.Menu, 'icon'):
                    icon = model.Menu.icon

            url = self.menu._get_admin_change_url(model)
            item = MenuItem(title=title, url=url, icon=icon)
            self.children.append(item)

        return True
