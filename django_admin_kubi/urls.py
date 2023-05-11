from django.urls import path
from django_admin_kubi import views

urlpatterns = [
    path("search/", views.search, name="kubi-search"),
    path("history/", views.history, name="kubi-history"),
]
