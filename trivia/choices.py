"""
Constantes compartidas de grados escolares chilenos (currículo escolar).

TextChoices define pares (valor_en_BD, etiqueta_legible). Se reutilizan
en CharField(choices=...) de Pregunta y PerfilEstudiante.
"""

from django.db import models


class GradoEscolar(models.TextChoices):
    """Chilean grades from 1° básico through 4° medio. / Códigos cortos → etiqueta UI."""

    # Sintaxis: NOMBRE = "valor_db", "etiqueta mostrada"
    PRIMERO_BASICO = "1B", "1° básico"
    SEGUNDO_BASICO = "2B", "2° básico"
    TERCERO_BASICO = "3B", "3° básico"
    CUARTO_BASICO = "4B", "4° básico"
    QUINTO_BASICO = "5B", "5° básico"
    SEXTO_BASICO = "6B", "6° básico"
    SEPTIMO_BASICO = "7B", "7° básico"
    OCTAVO_BASICO = "8B", "8° básico"
    PRIMERO_MEDIO = "1M", "1° medio"
    SEGUNDO_MEDIO = "2M", "2° medio"
    TERCERO_MEDIO = "3M", "3° medio"
    CUARTO_MEDIO = "4M", "4° medio"
