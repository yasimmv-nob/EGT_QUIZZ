"""
Modelos ORM de la app `trivia` (Phase 1).

En Django, cada clase que hereda de `models.Model` representa una tabla.
Los atributos (`CharField`, `ForeignKey`, …) son columnas; el ORM traduce
consultas Python a SQL. Tras cambiar modelos: `makemigrations` + `migrate`.
"""

from django.db import models

from .choices import GradoEscolar


class Categoria(models.Model):
    """Subject or topic grouping for trivia questions. / Agrupa preguntas por tema."""

    # CharField = texto corto; unique=True → índice UNIQUE en la BD.
    nombre = models.CharField(max_length=120, unique=True)
    # TextField = texto largo; blank=True permite dejarlo vacío en formularios/Admin.
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    # auto_now_add: se setea solo al crear; auto_now: se actualiza en cada save().
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        # Meta configura metadatos del modelo (no son columnas).
        verbose_name = "categoría"  # etiqueta singular en Admin
        verbose_name_plural = "categorías"
        ordering = ["nombre"]  # orden por defecto en QuerySets

    def __str__(self) -> str:
        # Cómo se muestra el objeto en Admin y el shell.
        return self.nombre


class Pregunta(models.Model):
    """A single trivia question scoped to a Chilean school grade."""

    # ForeignKey = relación N:1 (muchas preguntas → una categoría).
    # on_delete=CASCADE: si borro la categoría, se borran sus preguntas.
    # related_name="preguntas": acceso inverso → categoria.preguntas.all()
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="preguntas",
    )
    enunciado = models.TextField()
    # choices limita valores válidos; db_index acelera filtros por grado.
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
        # Índice compuesto: útil para listar preguntas activas de un grado.
        indexes = [
            models.Index(fields=["grado", "activa"]),
        ]

    def __str__(self) -> str:
        # get_grado_display() devuelve la etiqueta legible del TextChoices.
        preview = self.enunciado[:60] + ("…" if len(self.enunciado) > 60 else "")
        return f"[{self.get_grado_display()}] {preview}"


class OpcionRespuesta(models.Model):
    """One answer choice for a question; exactly one should be correct."""

    # N opciones por pregunta; related_name → pregunta.opciones.all()
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name="opciones",
    )
    texto = models.CharField(max_length=500)
    es_correcta = models.BooleanField(default=False)
    # PositiveSmallIntegerField: entero ≥ 0, ocupa poco espacio.
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "opción de respuesta"
        verbose_name_plural = "opciones de respuesta"
        ordering = ["pregunta", "orden", "id"]

    def __str__(self) -> str:
        mark = "✓" if self.es_correcta else "✗"
        return f"{mark} {self.texto[:80]}"
