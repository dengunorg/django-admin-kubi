from django.shortcuts import Http404
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django_admin_kubi.utils import get_kubi_feature


def get_searchable_models(request):
    """ Returns (model, perm,) for all models user can possibly see """
    items = []
    admin_site = admin.site

    for model, model_admin in admin_site._registry.items():
        search_fields = model_admin.get_search_fields(request)
        if not search_fields:
            continue

        # check permissions
        perms = model_admin.get_model_perms(request)
        if 'add' in perms:
            del perms['add']
        if True not in perms.values():
            continue
        items.append((model, model_admin, perms,))
    return items


def get_model_url_by_perm(opts, perms):
    info = opts.app_label, opts.model_name
    if 'change' in perms and perms['change']:
        return ('change', 'admin:%s_%s_change' % info)
    if 'delete' in perms and perms['delete']:
        return ('delete', 'admin:%s_%s_delete' % info)
    return None


def search(request):
    user = request.user

    if not request.method == "GET":
        raise Http404()

    if not (user.is_staff or user.is_superadmin):
        raise Http404()

    if not get_kubi_feature('ADMIN_SEARCH'):
        raise PermissionDenied

    search_term = request.GET.get("q", None)
    results = list()
    total_results = 0
    if search_term and len(search_term) >= 2:
        for model, model_admin, perms in get_searchable_models(request):
            queryset = model_admin.get_queryset(request)
            result = model_admin.get_search_results(request, queryset, search_term)[0]
            opts = model._meta
            if result:
                total_results += len(result)
                results.append({
                    'results': result,
                    'opts': opts,
                    'url': get_model_url_by_perm(opts, perms)
                })

    context = {
        'title': _('Search'),
        'term': search_term,
        'results': results,
        'total_results': total_results
    }
    return TemplateResponse(request, 'admin/search.html', context)


def history(request):
    from django_admin_kubi.admin import HistoryLogAdmin
    from django.contrib.admin.models import LogEntry

    user = request.user
    if not user.is_staff:
        raise Http404()

    if get_kubi_feature('ADMIN_HISTORY'):
        history_admin = HistoryLogAdmin(LogEntry, admin.site)
        return history_admin.changelist_view(request)

    raise PermissionDenied
