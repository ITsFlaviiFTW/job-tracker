# jobtracker/middleware.py
from django.conf import settings
from jobtracker.models import JobApplication

class DemoResetMiddleware:
    """Deletes all JobApplication rows after every request when DEMO_MODE=True."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if getattr(settings, "DEMO_MODE", False):
            JobApplication.objects.all().delete()
        return response
