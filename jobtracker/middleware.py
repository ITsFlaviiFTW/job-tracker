# jobtracker/middleware.py

from django.conf import settings
from jobtracker.models import JobApplication

class DemoResetMiddleware:
    """
    On the *first* GET in a demo session, delete all jobs.
    Subsequent GETs (including the POST→redirect) will preserve
    whatever the user just added.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only in demo mode, only on GET, and only once per session
        if getattr(settings, "DEMO_MODE", False) and request.method == "GET":
            if not request.session.get("demo_cleared"):
                JobApplication.objects.all().delete()
                request.session["demo_cleared"] = True

        return self.get_response(request)
