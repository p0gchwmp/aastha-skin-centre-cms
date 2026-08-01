"""Production-like settings for local browser quality audits.

The quality server uses WhiteNoise, compressed manifest assets and DEBUG=False
so Lighthouse measures the same delivery path as production. HTTPS-only cookie
and redirect settings are relaxed solely because the ephemeral CI server binds
to local HTTP.
"""

import os

os.environ.setdefault("SECRET_KEY", "quality-gate-only-not-for-production")

from .production import *  # noqa: F403, E402

DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8000"]
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
