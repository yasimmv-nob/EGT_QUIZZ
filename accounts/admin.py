"""
Admin de perfiles: inline en User + listado propio de PerfilEstudiante.

Patrón típico: extender UserAdmin con un StackedInline para editar el
perfil en la misma pantalla del usuario de auth.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import PerfilEstudiante


class PerfilEstudianteInline(admin.StackedInline):
    # StackedInline = campos apilados (vs TabularInline en tabla).
    model = PerfilEstudiante
    can_delete = False  # no borrar el perfil desde el form de User
    fk_name = "usuario"  # campo FK hacia User (por si hubiera varias FK)
    extra = 0  # no mostrar filas vacías extra
    fields = (
        "grado",
        "puntos",
        "penalizaciones",
        "racha_actual",
        "racha_maxima",
    )


class UserAdmin(BaseUserAdmin):
    # Hereda el Admin completo de User y añade el inline del perfil.
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
    # raw_id_fields: widget con ID + lupa (mejor con muchos usuarios).
    raw_id_fields = ("usuario",)


# Reemplazar el UserAdmin por defecto por el nuestro con inline.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
