from django.db import models

from .choices import GradoEscolar


class Categoria(models.Model):
    """Subject or topic grouping for trivia questions."""

    nombre = models.CharField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class Pregunta(models.Model):
    """A single trivia question scoped to a Chilean school grade."""

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="preguntas",
    )
    enunciado = models.TextField()
    grado = models.CharField(
        max_length=2,
        choices=GradoEscolar.choices,
        db_index=True,
        help_text="Nivel escolar chileno (1° básico – 4° medio).",
    )
    explicacion = models.TextField(
        blank=True,
        help_text="Opcional: explicación mostrada tras responder.",
    )
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "pregunta"
        verbose_name_plural = "preguntas"
        ordering = ["grado", "categoria", "id"]
        indexes = [
            models.Index(fields=["grado", "activa"]),
        ]

    def __str__(self) -> str:
        preview = self.enunciado[:60] + ("…" if len(self.enunciado) > 60 else "")
        return f"[{self.get_grado_display()}] {preview}"


class OpcionRespuesta(models.Model):
    """One answer choice for a question; exactly one should be correct."""

    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name="opciones",
    )
    texto = models.CharField(max_length=500)
    es_correcta = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "opción de respuesta"
        verbose_name_plural = "opciones de respuesta"
        ordering = ["pregunta", "orden", "id"]

    def __str__(self) -> str:
        mark = "✓" if self.es_correcta else "✗"
        return f"{mark} {self.texto[:80]}"
