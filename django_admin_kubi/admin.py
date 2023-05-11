from django.contrib import admin
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.template.defaultfilters import capfirst
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from functools import wraps


class HistoryLogActionFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Action')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'flag'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('1', _('Addition')),
            ('2', _('Change')),
            ('3', _('Deletion')),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(action_flag=1)
        if self.value() == '2':
            return queryset.filter(action_flag=2)
        if self.value() == '3':
            return queryset.filter(action_flag=3)


class HistoryLogAdmin(admin.ModelAdmin):
    actions = None
    list_per_page = 25
    list_display = ('action_time', 'user', 'content_display', 'repr_display', 'message_display')
    list_filter = ('user', 'content_type', HistoryLogActionFilter)
    search_fields = ('user__username', 'change_message')
    list_select_related = ('content_type', 'user',)
    list_max_show_all = False

    def message_display(self, obj):
        message = obj.get_change_message()
        if message:
            return message
        return '...'

    message_display.short_description = _('Message')

    def repr_display(self, obj):
        if obj.is_addition():
            icon = '<i class="fa fa-plus"></i>'
            cssclass = 'text-success'
        elif obj.is_change():
            icon = '<i class="fa fa-edit"></i>'
            cssclass = 'text-muted'
        elif obj.is_deletion():
            icon = '<i class="fa fa-trash"></i>'
            cssclass = 'text-danger'
        else:
            icon = ''

        if obj.is_deletion() or not obj.get_admin_url():
            link = obj.object_repr
        else:
            link = '<a href="%s">%s</a>' % (obj.get_admin_url(), obj.object_repr)

        return mark_safe('<span class="%s">%s %s</span>' % (cssclass, icon, link))

    repr_display.short_description = _('Entity')

    def content_display(self, obj):
        if obj.content_type:
            return capfirst(obj.content_type.name)
        else:
            return _('Unknown content')

    content_display.admin_order_field = 'content_type'
    content_display.short_description = _('Content')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        raise PermissionDenied

    def delete_view(self, request, object_id, extra_context=None):
        raise PermissionDenied

    def history_view(self, request, object_id, extra_context=None):
        raise PermissionDenied

    def get_urls(self):
        urlpatterns = []
        return urlpatterns


def context_data_for_app_index(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        response.context_data['app_label'] = kwargs.get('app_label')
        response.context_data['is_app_index'] = True
        response.context_data['admin_root_url'] = reverse('admin:index')
        return response
    return _wrapper

admin.site.__class__.app_index = context_data_for_app_index(admin.site.__class__.app_index)
