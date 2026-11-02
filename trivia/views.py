"""
Vistas DRF de trivia (Phase 2): listado filtrado + envío de respuestas.

Endpoints:
- GET  /api/categorias/
- GET  /api/preguntas/?grado=1B&categoria=<id>
- GET  /api/preguntas/<id>/
- POST /api/respuestas/
- GET  /api/perfil/
"""

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import PerfilEstudianteSerializer

from .choices import GradoEscolar
from .models import Categoria, Pregunta
from .permissions import HasStudentProfile
from .scoring import PUNTOS_POR_ACIERTO, aplicar_resultado_respuesta
from .serializers import (
    CategoriaSerializer,
    PreguntaSerializer,
    RespuestaResultadoSerializer,
    RespuestaSubmitSerializer,
)


class CategoriaListView(generics.ListAPIView):
    """GET: categorías activas (para filtros del cliente)."""

    permission_classes = [IsAuthenticated]
    serializer_class = CategoriaSerializer
    queryset = Categoria.objects.filter(activa=True).order_by("nombre")


class PreguntaListView(generics.ListAPIView):
    """
    GET: preguntas activas filtradas por grado (obligatorio) y categoría (opcional).

    Query params:
    - grado: código GradoEscolar, p.ej. `1B`, `4M` (required)
    - categoria: id numérico de Categoria (optional)
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PreguntaSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        grado = request.query_params.get("grado")
        if not grado:
            return Response(
                {
                    "grado": (
                        "Parámetro 'grado' obligatorio "
                        "(ej. 1B = 1° básico, 4M = 4° medio). "
                        "/ Query param 'grado' is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        valid_grados = {choice.value for choice in GradoEscolar}
        if grado not in valid_grados:
            return Response(
                {
                    "grado": (
                        f"Grado inválido '{grado}'. Valores: "
                        f"{', '.join(sorted(valid_grados))}. "
                        "/ Invalid grade code."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        # Prefetch opciones para evitar N+1 al serializar.
        qs = (
            Pregunta.objects.filter(activa=True)
            .select_related("categoria")
            .prefetch_related("opciones")
        )
        grado = self.request.query_params.get("grado")
        if grado:
            qs = qs.filter(grado=grado)

        categoria = self.request.query_params.get("categoria")
        if categoria:
            qs = qs.filter(categoria_id=categoria, categoria__activa=True)
        else:
            qs = qs.filter(categoria__activa=True)
        return qs


class PreguntaDetailView(generics.RetrieveAPIView):
    """GET: detalle de una pregunta activa con opciones públicas."""

    permission_classes = [IsAuthenticated]
    serializer_class = PreguntaSerializer
    queryset = (
        Pregunta.objects.filter(activa=True)
        .select_related("categoria")
        .prefetch_related("opciones")
    )


class RespuestaSubmitView(APIView):
    """
    POST: envía {pregunta, opcion}; el servidor valida y puntúa.

    Auth: usuario autenticado + PerfilEstudiante.
    El cuerpo NO acepta puntos ni flags de acierto — solo IDs.
    """

    permission_classes = [IsAuthenticated, HasStudentProfile]

    def post(self, request: Request) -> Response:
        serializer = RespuestaSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pregunta = serializer.validated_data["pregunta"]
        opcion = serializer.validated_data["opcion"]
        # Fuente de verdad: columna es_correcta en la BD (no el cliente).
        es_correcta = bool(opcion.es_correcta)

        perfil = request.user.perfil_estudiante
        puntos_obtenidos = aplicar_resultado_respuesta(
            perfil=perfil,
            es_correcta=es_correcta,
        )
        # Refrescar tras el save atómico dentro de aplicar_resultado_respuesta.
        perfil.refresh_from_db()

        payload = {
            "correcta": es_correcta,
            "puntos_obtenidos": puntos_obtenidos,
            "puntos_por_acierto": PUNTOS_POR_ACIERTO,
            # Feedback pedagógico tras responder (acierto o error).
            "explicacion": pregunta.explicacion,
            "perfil": perfil,
        }
        out = RespuestaResultadoSerializer(payload)
        return Response(out.data, status=status.HTTP_200_OK)


class PerfilEstudianteMeView(APIView):
    """GET: perfil gamificado del usuario autenticado."""

    permission_classes = [IsAuthenticated, HasStudentProfile]

    def get(self, request: Request) -> Response:
        perfil = request.user.perfil_estudiante
        return Response(PerfilEstudianteSerializer(perfil).data)
