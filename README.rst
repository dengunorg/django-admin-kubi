=================
DJANGO ADMIN KUBI
=================

Supports Django 4.0+

Django admin Kubi applies a face lift for the Django admin interface and mechanics. Its features include:

* A fast, attractive editor interface
* Complete Bootstrap 5 Templates
* Sass support for custom styling
* Font awesome
* Mobile friendly
* TinyMce Widget
* Admin with sidebar menu for easy navigation
* Admin Search View
* Admin LogEntry view
* django-modeltranslation support

Installation
============

* Download and install latest version of Django admin kubi:
.. code:: python

    pip install django-admin-kubi

* Add admin kubi to the INSTALLED_APPS in your project settings.py:
.. code:: python

    INSTALLED_APPS = (
        'django_admin_kubi',
        ...
        'django.contrib.admin',
    )

* Make sure ``django.template.context_processors.request`` context processor is enabled in settings.py (Django 1.8+ way):
.. code:: python

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    ...
                    'django.template.context_processors.request',
                    ...
                ],
            },
        },
    ]

* Add admin kubi urls to your project url patterns:
.. code:: python

    urlpatterns = patterns(
        ...
        path('admin/', include("django_admin_kubi.urls")),  # Django admin kubi URLS
        path('admin/', include(admin.site.urls)),
        ...
    )

Configuration settings
======================

* in your settings.py you can toggle features using the DJANGO_ADMIN_KUBI option.

.. code:: python

    DJANGO_ADMIN_KUBI = {
        'ADMIN_HISTORY': True,  # enables the history action panel
        'ADMIN_SEARCH': True,  # enables a full modal search
    }
