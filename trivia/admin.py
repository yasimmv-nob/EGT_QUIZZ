"""
Registro en Django Admin de los modelos de trivia.

Admin genera una UI CRUD a partir de ModelAdmin. Los "inlines" permiten
editar modelos relacionados (FK) en la misma página del padre.
"""

from django.contrib import admin

from .models import Categoria, OpcionRespuesta, Pregunta


class OpcionRespuestaInline(admin.TabularInline):
    # TabularInline = tabla compacta embebida en el form de Pregunta.
    model = OpcionRespuesta
    extra = 4  # filas vacías extra al crear una pregunta nueva
    fields = ("texto", "es_correcta", "orden")
    ordering = ("orden", "id")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    # list_display: columnas en la lista; list_filter / search_fields: barra lateral y búsqueda.
    list_display = ("nombre", "activa", "actualizado_en")
    list_filter = ("activa",)
    search_fields = ("nombre", "descripcion")
    ordering = ("nombre",)


@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ("enunciado_corto", "categoria", "grado", "activa", "actualizado_en")
    list_filter = ("grado", "categoria", "activa")
    search_fields = ("enunciado", "explicacion")
    # list_select_related: JOIN anticipado → evita N+1 al mostrar la FK.
    list_select_related = ("categoria",)
    inlines = (OpcionRespuestaInline,)  # editar opciones dentro de la pregunta
    ordering = ("grado", "categoria", "id")

    @admin.display(description="Enunciado")
    def enunciado_corto(self, obj: Pregunta) -> str:
        # Método custom como columna de list_display (no es un field del modelo).
        return obj.enunciado[:80] + ("…" if len(obj.enunciado) > 80 else "")


@admin.register(OpcionRespuesta)
class OpcionRespuestaAdmin(admin.ModelAdmin):
    # También registramos el modelo solo, por si se edita fuera del inline.
    list_display = ("texto_corto", "pregunta", "es_correcta", "orden")
    # Filtros por campos relacionados: doble underscore = lookup ORM.
    list_filter = ("es_correcta", "pregunta__grado", "pregunta__categoria")
    search_fields = ("texto", "pregunta__enunciado")
    list_select_related = ("pregunta", "pregunta__categoria")
    ordering = ("pregunta", "orden", "id")

    @admin.display(description="Texto")
    def texto_corto(self, obj: OpcionRespuesta) -> str:
        return obj.texto[:80] + ("…" if len(obj.texto) > 80 else "")
