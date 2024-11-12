from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class SetupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # redirect to the setup page if no users exist
        if request.path == reverse('admin:login'):
            if User.objects.count() == 0:
                return redirect('kubi-setup')

        return self.get_response(request)
