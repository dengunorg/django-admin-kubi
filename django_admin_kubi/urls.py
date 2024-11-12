from django.urls import path
from django_admin_kubi import views
from django_admin_kubi.utils import is_setup_flow_enabled


urlpatterns = [
    path("search/", views.search, name="kubi-search"),
    path("history/", views.history, name="kubi-history"),
]

if is_setup_flow_enabled():
    urlpatterns += [
        path("setup/", views.setup_view, name="kubi-setup"),
    ]
