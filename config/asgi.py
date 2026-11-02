"""
ASGI entrypoint (async / websockets: uvicorn, Daphne).

Misma idea que wsgi.py, pero para el protocolo ASGI.
Phase 1 usa WSGI vía runserver; este archivo queda listo para deploy async.
Docs: https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
