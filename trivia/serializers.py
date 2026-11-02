"""
Serializers DRF de trivia (Phase 2).

Importante de seguridad: `OpcionPublicaSerializer` NO incluye `es_correcta`.
La corrección se evalúa solo en el servidor al hacer POST /api/respuestas/.
"""

from rest_framework import serializers

from accounts.serializers import PerfilEstudianteSerializer

from .models import Categoria, OpcionRespuesta, Pregunta
from .scoring import PUNTOS_POR_ACIERTO


class CategoriaSerializer(serializers.ModelSerializer):
    """Active category for filters / pickers. / Categoría para filtros."""

    class Meta:
        model = Categoria
        fields = ("id", "nombre", "descripcion")


class OpcionPublicaSerializer(serializers.ModelSerializer):
    """
    Opción visible al estudiante.

    Deliberately omits `es_correcta` so clients cannot cheat by reading the flag.
    """

    class Meta:
        model = OpcionRespuesta
        fields = ("id", "texto", "orden")


class PreguntaSerializer(serializers.ModelSerializer):
    """Pregunta con opciones públicas (sin marcar la correcta)."""

    categoria = CategoriaSerializer(read_only=True)
    opciones = OpcionPublicaSerializer(many=True, read_only=True)
    grado_display = serializers.CharField(source="get_grado_display", read_only=True)

    class Meta:
        model = Pregunta
        fields = (
            "id",
            "enunciado",
            "grado",
            "grado_display",
            "categoria",
            "opciones",
        )


class RespuestaSubmitSerializer(serializers.Serializer):
    """
    Payload del estudiante al responder.

    Solo acepta IDs. Cualquier `puntos` / `correcta` del cliente se ignora
    (ni siquiera existen como campos).
    """

    pregunta = serializers.PrimaryKeyRelatedField(
        queryset=Pregunta.objects.filter(activa=True).select_related("categoria"),
    )
    opcion = serializers.PrimaryKeyRelatedField(
        queryset=OpcionRespuesta.objects.select_related("pregunta"),
    )

    def validate(self, attrs: dict) -> dict:
        # Cross-field: la opción debe pertenecer a la pregunta enviada.
        pregunta: Pregunta = attrs["pregunta"]
        opcion: OpcionRespuesta = attrs["opcion"]
        if opcion.pregunta_id != pregunta.id:
            raise serializers.ValidationError(
                {
                    "opcion": (
                        "La opción no pertenece a la pregunta indicada. "
                        "/ Option does not belong to the given question."
                    )
                }
            )
        return attrs


class RespuestaResultadoSerializer(serializers.Serializer):
    """Respuesta del servidor tras puntuar (solo salida)."""

    correcta = serializers.BooleanField()
    puntos_obtenidos = serializers.IntegerField()
    puntos_por_acierto = serializers.IntegerField(default=PUNTOS_POR_ACIERTO)
    explicacion = serializers.CharField(allow_blank=True)
    perfil = PerfilEstudianteSerializer()
