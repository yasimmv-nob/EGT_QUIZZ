"""
Modelos de la app `accounts`: perfil de estudiante (gamificación).

OneToOneField enlaza 1:1 con el User de Django (AUTH_USER_MODEL),
extensión clásica del perfil sin sustituir el modelo de usuario.
"""

from django.conf import settings
from django.db import models

from trivia.choices import GradoEscolar


class PerfilEstudiante(models.Model):
    """Student profile with gamification counters (points, penalties, streaks)."""

    # OneToOneField: un perfil por usuario; CASCADE borra el perfil si se borra el User.
    # settings.AUTH_USER_MODEL evita acoplarse a auth.User hardcodeado.
    # related_name → user.perfil_estudiante
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_estudiante",
    )
    grado = models.CharField(
        max_length=2,
        choices=GradoEscolar.choices,
        db_index=True,
        help_text="Grado escolar actual del estudiante.",
    )
    # PositiveIntegerField: entero ≥ 0 (puntos / contadores no negativos).
    puntos = models.PositiveIntegerField(default=0)
    penalizaciones = models.PositiveIntegerField(
        default=0,
        help_text="Contador de respuestas incorrectas / penalizaciones aplicadas.",
    )
    racha_actual = models.PositiveIntegerField(
        default=0,
        help_text="Aciertos consecutivos actuales.",
    )
    racha_maxima = models.PositiveIntegerField(
        default=0,
        help_text="Mejor racha de aciertos consecutivos.",
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "perfil de estudiante"
        verbose_name_plural = "perfiles de estudiante"
        # "-" = orden descendente (más puntos primero).
        ordering = ["-puntos", "usuario__username"]

    def __str__(self) -> str:
        return f"{self.usuario.get_username()} ({self.get_grado_display()}) — {self.puntos} pts"
