# config/settings/demo.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["demo.jobtracker.flavstudios.dev"]

# In-memory SQLite resets on each restart
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

DEMO_MODE = True
