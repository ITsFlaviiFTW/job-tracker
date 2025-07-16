# config/settings/demo.py
from .base import *
from .base import MIDDLEWARE as BASE_MIDDLEWARE

DEBUG = True
ALLOWED_HOSTS = ["demo-jobtracker.flavstudios.dev"]

# Persist demo data in a file so we can migrate once
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "demo.sqlite3",
    }
}

DEMO_MODE = True



MIDDLEWARE = [
    mw for mw in BASE_MIDDLEWARE
    if mw != "django.middleware.clickjacking.XFrameOptionsMiddleware"
]
