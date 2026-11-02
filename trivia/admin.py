from django.contrib import admin

from .models import Categoria, OpcionRespuesta, Pregunta


class OpcionRespuestaInline(admin.TabularInline):
    model = OpcionRespuesta
    extra = 4
    fields = ("texto", "es_correcta", "orden")
    ordering = ("orden", "id")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activa", "actualizado_en")
    list_filter = ("activa",)
    search_fields = ("nombre", "descripcion")
    ordering = ("nombre",)


@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ("enunciado_corto", "categoria", "grado", "activa", "actualizado_en")
    list_filter = ("grado", "categoria", "activa")
    search_fields = ("enunciado", "explicacion")
    list_select_related = ("categoria",)
    inlines = (OpcionRespuestaInline,)
    ordering = ("grado", "categoria", "id")

    @admin.display(description="Enunciado")
    def enunciado_corto(self, obj: Pregunta) -> str:
        return obj.enunciado[:80] + ("…" if len(obj.enunciado) > 80 else "")


@admin.register(OpcionRespuesta)
class OpcionRespuestaAdmin(admin.ModelAdmin):
    list_display = ("texto_corto", "pregunta", "es_correcta", "orden")
    list_filter = ("es_correcta", "pregunta__grado", "pregunta__categoria")
    search_fields = ("texto", "pregunta__enunciado")
    list_select_related = ("pregunta", "pregunta__categoria")
    ordering = ("pregunta", "orden", "id")

    @admin.display(description="Texto")
    def texto_corto(self, obj: OpcionRespuesta) -> str:
        return obj.texto[:80] + ("…" if len(obj.texto) > 80 else "")
