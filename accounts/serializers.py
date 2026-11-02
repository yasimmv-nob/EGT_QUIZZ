"""
Serializers DRF del perfil de estudiante.

Exponen el estado de gamificación que el cliente puede mostrar,
pero nunca aceptan puntos/rachas desde el request (solo lectura).
"""

from rest_framework import serializers

from .models import PerfilEstudiante


class PerfilEstudianteSerializer(serializers.ModelSerializer):
    """Read-only snapshot of student gamification counters. / Solo lectura."""

    # get_grado_display() → etiqueta legible ("1° básico").
    grado_display = serializers.CharField(source="get_grado_display", read_only=True)
    username = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = PerfilEstudiante
        fields = (
            "id",
            "username",
            "grado",
            "grado_display",
            "puntos",
            "penalizaciones",
            "racha_actual",
            "racha_maxima",
        )
        # read_only_fields refuerza que el cliente no puede mutar contadores aquí.
        read_only_fields = fields
