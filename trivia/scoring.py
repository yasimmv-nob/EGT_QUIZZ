"""
Puntuación estrictamente en el servidor (Phase 2).

El cliente solo envía IDs de pregunta/opción. Nunca confiamos en un flag
`correcta` ni en puntos enviados desde el front: leemos `es_correcta` en BD
y actualizamos `PerfilEstudiante` aquí.
"""

from __future__ import annotations

from django.db import transaction

from accounts.models import PerfilEstudiante

# Constantes de gamificación simples (Fase 4 puede afinar la economía).
# / Simple reward constants — keep learning-focused, not deep game economies.
PUNTOS_POR_ACIERTO = 10


@transaction.atomic
def aplicar_resultado_respuesta(
    *,
    perfil: PerfilEstudiante,
    es_correcta: bool,
) -> int:
    """
    Actualiza puntos, penalizaciones y rachas según el resultado.

    Returns the points awarded this turn (0 if incorrect).
    Usa select_for_update vía el caller para evitar condiciones de carrera.
    """
    # Bloqueo pesimista del perfil dentro de la transacción.
    perfil = (
        PerfilEstudiante.objects.select_for_update()
        .get(pk=perfil.pk)
    )

    puntos_obtenidos = 0
    if es_correcta:
        puntos_obtenidos = PUNTOS_POR_ACIERTO
        perfil.puntos += puntos_obtenidos
        perfil.racha_actual += 1
        if perfil.racha_actual > perfil.racha_maxima:
            perfil.racha_maxima = perfil.racha_actual
    else:
        # Incorrecta: suma penalización y rompe la racha actual.
        perfil.penalizaciones += 1
        perfil.racha_actual = 0

    perfil.save(
        update_fields=[
            "puntos",
            "penalizaciones",
            "racha_actual",
            "racha_maxima",
            "actualizado_en",
        ]
    )
    return puntos_obtenidos
