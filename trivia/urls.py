"""
Rutas de la API de trivia (incluidas desde config.urls bajo /api/).

path() → vista basada en clase vía .as_view() (patrón DRF/Django).
"""

from django.urls import path

from .views import (
    CategoriaListView,
    PerfilEstudianteMeView,
    PreguntaDetailView,
    PreguntaListView,
    RespuestaSubmitView,
)

urlpatterns = [
    path("categorias/", CategoriaListView.as_view(), name="api-categorias"),
    path("preguntas/", PreguntaListView.as_view(), name="api-preguntas"),
    path(
        "preguntas/<int:pk>/",
        PreguntaDetailView.as_view(),
        name="api-pregunta-detail",
    ),
    path("respuestas/", RespuestaSubmitView.as_view(), name="api-respuestas"),
    path("perfil/", PerfilEstudianteMeView.as_view(), name="api-perfil"),
]
