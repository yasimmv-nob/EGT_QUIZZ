from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import PerfilEstudiante


class PerfilEstudianteInline(admin.StackedInline):
    model = PerfilEstudiante
    can_delete = False
    fk_name = "usuario"
    extra = 0
    fields = (
        "grado",
        "puntos",
        "penalizaciones",
        "racha_actual",
        "racha_maxima",
    )


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilEstudianteInline,)


@admin.register(PerfilEstudiante)
class PerfilEstudianteAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "grado",
        "puntos",
        "penalizaciones",
        "racha_actual",
        "racha_maxima",
        "actualizado_en",
    )
    list_filter = ("grado",)
    search_fields = ("usuario__username", "usuario__email", "usuario__first_name")
    list_select_related = ("usuario",)
    ordering = ("-puntos", "usuario__username")
    raw_id_fields = ("usuario",)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
