"""
URLconf raíz del proyecto (ROOT_URLCONF = config.urls).

`urlpatterns` mapea rutas URL → vistas o includes de otras apps.
Phase 1: Admin. Phase 2: API DRF bajo /api/.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # /admin/ → sitio de administración (ModelAdmins registrados en cada app).
    path("admin/", admin.site.urls),
    # /api/ → endpoints DRF (listado, respuestas, perfil).
    path("api/", include("trivia.urls")),
]
