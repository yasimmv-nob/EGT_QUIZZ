"""
URLconf raíz del proyecto (ROOT_URLCONF = config.urls).

`urlpatterns` mapea rutas URL → vistas o includes de otras apps.
Phase 1 solo monta Admin; Phase 2 añadirá rutas de la API DRF.
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    # /admin/ → sitio de administración (ModelAdmins registrados en cada app).
    path("admin/", admin.site.urls),
]
