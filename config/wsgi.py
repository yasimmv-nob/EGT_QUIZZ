"""
WSGI entrypoint (servidores sync: gunicorn, runserver).

`application` es el callable que el servidor web invoca por request.
DJANGO_SETTINGS_MODULE debe apuntar a config.settings.
Docs: https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
