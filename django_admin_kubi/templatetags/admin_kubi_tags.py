from __future__ import unicode_literals

import hashlib
import urllib
import re

from django import template
from django.db import models
from django.http import QueryDict
from django.utils import formats
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import Truncator, capfirst
from django.utils.translation import gettext_lazy as _
from django.utils.module_loading import import_string
from django.template import defaultfilters
from django.contrib.admin.views.main import PAGE_VAR
from django_admin_kubi.admin_menu.items import get_model_icon_overwrites
from django_admin_kubi.utils import get_kubi_feature
from django.utils.timezone import is_aware
import datetime

from django.utils.translation import (
    gettext_lazy,
    ngettext,
    ngettext_lazy,
    npgettext_lazy,
    pgettext,
    round_away_from_one,
)

register = template.Library()


@register.simple_tag()
def has_kubi_feature(feature_name):
    return get_kubi_feature(feature_name)


def get_admin_menu():
    """
    Returns the admin menu defined by the user or the default one.
    """
    menu_cls = getattr(
        settings,
        'ADMIN_MENU',
        'django_admin_kubi.admin_menu.menu.AdminMenu'
    )

    MENU = import_string(menu_cls)
    return MENU()


@register.inclusion_tag('admin/sidebar_menu.html', takes_context=True)
def admin_menu(context):

    menu = get_admin_menu()
    menu.set_context(context)

    # RENDER MENU
    context.update({
        'menu': menu
    })
    return context


def silence_without_field(fn):
    def wrapped(field, attr):
        if not field:
            return ""
        else:
            return fn(field, attr)
    return wrapped


def _process_field_attributes(field, attr, process):
    # split attribute name and value from 'attr:value' string
    params = attr.split(':', 1)
    attribute = params[0]
    value = params[1] if len(params) == 2 else ''

    # decorate field.as_widget method with updated attributes
    old_as_widget = field.as_widget

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        attrs = attrs or {}
        process(widget or self.field.widget, attrs, attribute, value)
        return old_as_widget(widget, attrs, only_initial)

    bound_method = type(old_as_widget)
    try:
        field.as_widget = bound_method(as_widget, field, field.__class__)
    except TypeError:
        field.as_widget = bound_method(as_widget, field)
    return field


@register.filter("append_attr")
@silence_without_field
def append_attr(field, attr):
    def process(widget, attrs, attribute, value):
        if attrs.get(attribute):
            attrs[attribute] += ' ' + value
        elif widget.attrs.get(attribute):
            attrs[attribute] = widget.attrs[attribute] + ' ' + value
        else:
            attrs[attribute] = value
    return _process_field_attributes(field, attr, process)


@register.filter("label_tag")
def label_tag(field, css_class=None):
    if css_class is None:
        css_class = ''
    output = ""
    if isinstance(field, dict):
        output = u'<label class="form-label %s">%s:</label>' % (css_class, field.label)
    else:
        if field.field.required:
            output = u'<label for="%s" class="form-label %s required">%s: <small class="text-required">*</small></label>' % (field.id_for_label, css_class, field.label)
        else:
            output = u'<label for="%s" class="form-label %s">%s:</label>' % (field.id_for_label, css_class, field.label)

    return mark_safe(output)


@register.filter("line_class")
def line_class(fields):
    l = len(fields)
    if l > 1:
        size = int(12/l)
        if size < 1:
            size = 1
        return "col-md-%s col-lg-%s" % (size, size)
    return ""


@register.filter("add_class")
@silence_without_field
def add_class(field, css_class):
    return append_attr(field, 'class:' + css_class)


@register.filter("add_placeholder")
@silence_without_field
def add_placeholder(field, placeholder_value):
    return append_attr(field, 'placeholder:' + placeholder_value)


@register.filter(name='widget_type')
def widget_type(field):
    """
    Template filter that returns field widget class name (in lower case).
    E.g. if field's widget is TextInput then {{ field|widget_type }} will
    return 'textinput'.
    """
    if hasattr(field, 'field') and hasattr(field.field, 'widget') and field.field.widget:
        if hasattr(field.field.widget, 'widget') and field.field.widget.widget:
            return field.field.widget.widget.__class__.__name__.lower()
        return field.field.widget.__class__.__name__.lower()
    return ''


@register.filter
def gravatar_url(email, size=40):
    """
    returns gravatar url based on provided email
    Usage: {{ email|gravatar_url:150 }}
    """
    default = "identicon"
    return "https://www.gravatar.com/avatar/%s?%s" % (hashlib.md5(email.lower().encode('utf-8')).hexdigest(), urllib.parse.urlencode({'d': default, 's': str(size)}))


# return an image tag with the gravatar
# TEMPLATE USE:  {{ email|gravatar:150 }}
@register.filter
def gravatar(email, size=40):
    url = gravatar_url(email, size)
    return mark_safe('<img src="%s">' % url)


@register.filter
def user_avatar(user):
    initials = None
    if user.first_name and user.last_name:
        initials = "%s%s" % (user.first_name[0], user.last_name[0])
    elif user.first_name:
        initials = "%s%s" % (user.first_name[0], user.first_name[1])
    elif user.last_name:
        initials = "%s%s" % (user.last_name[0], user.last_name[1])

    if user.email:
        image = gravatar(user.email, size=60)
        output = '<div class="avatar gravatar">%s</div>' % image
    elif initials:
        output = '<div class="avatar initials">%s</div>' % initials.upper()
    else:
        output = '<div class="avatar icon"><i class="fa fa-leaf"></i></div>'

    return mark_safe(output)


@register.filter
def user_short_name(user):
    output = []
    if user.first_name:
        output += re.sub("[^\w]", " ",  user.first_name).split()
    if user.last_name:
        output += re.sub("[^\w]", " ",  user.last_name).split()

    if not output:
        output = [user.username if hasattr(user, 'username') else user.email]

    try:
        first_part = output[:1][0]
        second_part = output[-1:][0]
        if first_part == second_part:
            output = first_part
        else:
            output = "%s %s." % (first_part, second_part[0])
    except:
        output = user.username if hasattr(user, 'username') else user.email

    return mark_safe(output)


@register.filter("user_type")
def user_type(user):
    if user.is_superuser:
        output = _('Administrator')
    elif user.is_staff:
        output = _('Staff')
    else:
        output = _('User')

    return mark_safe(output)


@register.filter
def user_admin_urlname(value, arg):
    """
    Providing a link to change the user
    (for working better with auth custom user)
    """
    return 'admin:%s_%s_%s' % (value._meta.app_label, value._meta.model_name, arg)


@register.filter(is_safe=True)
@defaultfilters.stringfilter
def truncate_title(value):
    """
    Truncates the title to a specific char size.
    """
    return Truncator(value).chars(32)


@register.simple_tag
def breadcrumbs_icon(options):
    """
    Returns a font awesome icon to be used in the breadcrumbs block
    """
    model = None
    icon = "fa-default"
    if isinstance(options, models.Model):
        model = options
    elif hasattr(options, 'model'):
        model = options.model
    elif isinstance(options, str):
        icon = options
    if model and get_model_icon_overwrites(model):
        icon = get_model_icon_overwrites(model)
    if model and hasattr(model, 'Menu'):
        if hasattr(model.Menu, 'icon'):
            icon = model.Menu.icon
    return mark_safe('<span class="breadcrumb-icon"><i class="fa %s"></i></span>' % icon)


@register.simple_tag
def paginator_number(cl, i):
    """
    Generates an individual page index link in a paginated list.
    """
    if i == '.':
        return format_html(u'<li class="page-item disabled"><span class="page-link">...</span></li>')
    elif i == cl.page_num:
        return format_html(u'<li class="page-item active"><span class="page-link">{0}</span></li> ', i)
    else:
        return format_html(u'<li class="page-item"><a class="page-link" href="{0}"{1}>{2}</a></li>', cl.get_query_string({PAGE_VAR: i}), mark_safe(' class="end"' if i == cl.paginator.num_pages-1 else ''), i)


class AdminLogNode(template.Node):
    """
        NOTE: I've changed the original behaviour in order to provide a
        Admin Log for a specific app on the AdminSite.app_index.
    """
    def __init__(self, limit, varname, user):
        self.limit, self.varname, self.user = limit, varname, user

    def __repr__(self):
        return "<GetAdminLog Node>"

    def render(self, context):
        from django.contrib.admin.models import LogEntry

        app_label = context.get('app_label')
        if app_label:
            if self.user is None:
                context[self.varname] = LogEntry.objects.filter(content_type__app_label__exact=app_label).select_related('content_type', 'user')[:self.limit]
            else:
                user_id = self.user
                if not user_id.isdigit():
                    user_id = context[self.user].id
                context[self.varname] = LogEntry.objects.filter(user__id__exact=user_id, content_type__app_label__exact=app_label).select_related('content_type', 'user')[:int(self.limit)]
        return ''


@register.tag
def get_admin_log_for_app(parser, token):
    """
    NOTE: I've changed the original behaviour in order to provide a
    Admin Log for a specific app on the AdminSite.app_index.

    Populates a template variable with the admin log for the given criteria.

    Usage::

        {% get_admin_log_for_app [limit] as [varname] for_user [context_var_containing_user_obj] %}

    Examples::

        {% get_admin_log_for_app 10 as admin_log for_user 23 %}
        {% get_admin_log_for_app 10 as admin_log for_user user %}
        {% get_admin_log_for_app 10 as admin_log %}

    Note that ``context_var_containing_user_obj`` can be a hard-coded integer
    (user ID) or the name of a template context variable containing the user
    object whose ID you want.
    """
    tokens = token.contents.split()
    if len(tokens) < 4:
        raise template.TemplateSyntaxError(
            "'get_admin_log_for_app' statements require two arguments")
    if not tokens[1].isdigit():
        raise template.TemplateSyntaxError(
            "First argument to 'get_admin_log_for_app' must be an integer")
    if tokens[2] != 'as':
        raise template.TemplateSyntaxError(
            "Second argument to 'get_admin_log_for_app' must be 'as'")
    if len(tokens) > 4:
        if tokens[4] != 'for_user':
            raise template.TemplateSyntaxError(
                "Fourth argument to 'get_admin_log_for_app' must be 'for_user'")
    return AdminLogNode(limit=tokens[1], varname=tokens[3], user=(len(tokens) > 5 and tokens[5] or None))


@register.simple_tag(takes_context=True)
def get_fieldsets_and_inlines(context):
    """
    USAGE:
    In ModelAdmin()
    -----------------------------
    (i | inline)   :Show inline
    (f | fieldset) :Show filedset
    -----------------------------
    eg:
    list_fieldsets_inlines_order = ('i', 'inline', 'i', 'fielset', 'f')
    """

    adminform = context['adminform']
    model_admin = adminform.model_admin
    adminform = iter(adminform)

    # Check if has inlines, can be a custom admin view
    inlines = iter([])
    if 'inline_admin_formsets' in context:
        inlines = iter(context['inline_admin_formsets'])

    obj = None
    if 'original'in context:
        obj = context['original']

    request = QueryDict()
    if 'request'in context:
        request = context['request']

    # Get Order
    list_fieldsets_inlines_order = ()
    if hasattr(model_admin, 'list_fieldsets_inlines_order'):
        list_fieldsets_inlines_order = model_admin.list_fieldsets_inlines_order

    if hasattr(model_admin, 'get_list_fieldsets_inlines_order'):
        list_fieldsets_inlines_order = model_admin.get_list_fieldsets_inlines_order(request, obj=obj)

    # Create MIX
    fieldsets_and_inlines = []
    for choice in list_fieldsets_inlines_order:

        if choice in ('f', 'fieldset'):

            try:
                fieldsets_and_inlines.append(('fieldset', adminform.__next__()))
            except StopIteration:
                pass

        elif choice in ('i', 'inline'):

            try:
                fieldsets_and_inlines.append(('inline', inlines.__next__()))
            except StopIteration:
                pass

    for fieldset in adminform:
        fieldsets_and_inlines.append(('fieldset', fieldset))

    for inline in inlines:
        fieldsets_and_inlines.append(('inline', inline))

    return fieldsets_and_inlines


@register.inclusion_tag('admin/date_hierarchy.html')
def date_hierarchy(cl):
    """
    Displays the date hierarchy for date drill-down functionality.
    """
    if cl.date_hierarchy:
        field_name = cl.date_hierarchy
        year_field = '%s__year' % field_name
        month_field = '%s__month' % field_name
        day_field = '%s__day' % field_name
        field_generic = '%s__' % field_name
        year_lookup = cl.params.get(year_field)
        month_lookup = cl.params.get(month_field)
        day_lookup = cl.params.get(day_field)
        one_year_only = False
        one_month_only = False

        def link(filters):
            return cl.get_query_string(filters, [field_generic])

        if not (year_lookup or month_lookup or day_lookup):
            # select appropriate start level
            date_range = cl.queryset.aggregate(first=models.Min(field_name),
                                               last=models.Max(field_name))
            if date_range['first'] and date_range['last']:
                if date_range['first'].year == date_range['last'].year:
                    year_lookup = date_range['first'].year
                    one_year_only = True
                    if date_range['first'].month == date_range['last'].month:
                        month_lookup = date_range['first'].month
                        one_month_only = True

        if year_lookup and month_lookup and day_lookup:
            day = datetime.date(int(year_lookup), int(month_lookup), int(day_lookup))
            return {
                'show': True,
                'back': {
                    'link': link({year_field: year_lookup, month_field: month_lookup}),
                    'title': capfirst(formats.date_format(day, 'YEAR_MONTH_FORMAT'))
                },
                'choice': capfirst(formats.date_format(day)),
            }
        elif year_lookup and month_lookup:
            days = getattr(cl.queryset, 'dates')(field_name, 'day')
            cday = datetime.date(int(year_lookup), int(month_lookup), int(1))
            return {
                'show': True,
                'back': {
                    'link': link({year_field: year_lookup}),
                    'title': str(year_lookup)
                } if not one_month_only else {},
                'choice': capfirst(formats.date_format(cday, 'YEAR_MONTH_FORMAT')),
                'choices': [{
                    'link': link({year_field: year_lookup, month_field: month_lookup, day_field: day.day}),
                    'title': capfirst(formats.date_format(day, 'j - l'))
                } for day in days]
            }
        elif year_lookup:
            months = getattr(cl.queryset, 'dates')(field_name, 'month')
            return {
                'show': True,
                'back': {
                    'link': link({}),
                    'title': _('All dates')
                } if not one_year_only else {},
                'choice': str(year_lookup),
                'choices': [{
                    'link': link({year_field: year_lookup, month_field: month.month}),
                    'title': capfirst(formats.date_format(month, 'F'))
                } for month in months]
            }
        else:
            years = getattr(cl.queryset, 'dates')(field_name, 'year')
            return {
                'show': len(years) > 0,
                'choices': [{
                    'link': link({year_field: str(year.year)}),
                    'title': str(year.year),
                } for year in years]
            }


@register.filter
def naturaltimeshort(value):
    return NaturalTimeShortFormatter.string_for(value)


class NaturalTimeShortFormatter:
    time_strings = {
        # Translators: delta will contain a string like '2 months' or '1 month, 2 weeks'
        "past-day": gettext_lazy("%(delta)s"),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        "past-hour": ngettext_lazy("1h", "%(count)sh", "count"),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        "past-minute": ngettext_lazy("1m", "%(count)sm", "count"),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        "past-second": ngettext_lazy("1s", "%(count)ss", "count"),
        "now": gettext_lazy("now"),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        "future-second": ngettext_lazy(
            "in 1s", "in %(count)ss", "count"
        ),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        "future-minute": ngettext_lazy(
            "in 1m", "in %(count)sm", "count"
        ),
        # Translators: please keep a non-breaking space (U+00A0) between count
        # and time unit.
        "future-hour": ngettext_lazy(
            "in 1h", "in %(count)sh", "count"
        ),
        # Translators: delta will contain a string like '2 months' or '1 month, 2 weeks'
        "future-day": gettext_lazy("in %(delta)s"),
    }
    past_substrings = {
        # Translators: 'naturaltime-past' strings will be included in '%(delta)s ago'
        "year": npgettext_lazy(
            "naturaltimeshort-past", "%(num)dy", "%(num)d y", "num"
        ),
        "month": npgettext_lazy(
            "naturaltimeshort-past", "%(num)dmo", "%(num)dmo", "num"
        ),
        "week": npgettext_lazy(
            "naturaltimeshort-past", "%(num)dw", "%(num)dw", "num"
        ),
        "day": npgettext_lazy("naturaltime-past", "%(num)dd", "%(num)dd", "num"),
        "hour": npgettext_lazy(
            "naturaltimeshort-past", "%(num)dh", "%(num)dh", "num"
        ),
        "minute": npgettext_lazy(
            "naturaltimeshort-past", "%(num)dm", "%(num)dm", "num"
        ),
    }
    future_substrings = {
        # Translators: 'naturaltime-future' strings will be included in
        # '%(delta)s from now'.
        "year": npgettext_lazy(
            "naturaltimeshort-future", "%(num)dy", "%(num)dy", "num"
        ),
        "month": npgettext_lazy(
            "naturaltimeshort-future", "%(num)dmo", "%(num)dmo", "num"
        ),
        "week": npgettext_lazy(
            "naturaltimeshort-future", "%(num)dw", "%(num)dw", "num"
        ),
        "day": npgettext_lazy(
            "naturaltimeshort-future", "%(num)dd", "%(num)dd", "num"
        ),
        "hour": npgettext_lazy(
            "naturaltimeshort-future", "%(num)dh", "%(num)dh", "num"
        ),
        "minute": npgettext_lazy(
            "naturaltimeshort-future", "%(num)dm", "%(num)dm", "num"
        ),
    }

    @classmethod
    def string_for(cls, value):
        if not isinstance(value, datetime.date):  # datetime is a subclass of date
            return value

        now = datetime.datetime.now(datetime.timezone.utc if is_aware(value) else None)
        if value < now:
            delta = now - value
            if delta.days != 0:
                return cls.time_strings["past-day"] % {
                    "delta": defaultfilters.timesince(
                        value, now, time_strings=cls.past_substrings
                    ),
                }
            elif delta.seconds == 0:
                return cls.time_strings["now"]
            elif delta.seconds < 60:
                return cls.time_strings["past-second"] % {"count": delta.seconds}
            elif delta.seconds // 60 < 60:
                count = delta.seconds // 60
                return cls.time_strings["past-minute"] % {"count": count}
            else:
                count = delta.seconds // 60 // 60
                return cls.time_strings["past-hour"] % {"count": count}
        else:
            delta = value - now
            if delta.days != 0:
                return cls.time_strings["future-day"] % {
                    "delta": defaultfilters.timeuntil(
                        value, now, time_strings=cls.future_substrings
                    ),
                }
            elif delta.seconds == 0:
                return cls.time_strings["now"]
            elif delta.seconds < 60:
                return cls.time_strings["future-second"] % {"count": delta.seconds}
            elif delta.seconds // 60 < 60:
                count = delta.seconds // 60
                return cls.time_strings["future-minute"] % {"count": count}
            else:
                count = delta.seconds // 60 // 60
                return cls.time_strings["future-hour"] % {"count": count}
