"""
Permisos DRF orientados al perfil de estudiante.

Assumption / Supuesto de auth (Phase 2):
- Toda la API exige usuario autenticado (sesión o Basic; ver settings).
- Responder y ver el propio perfil exige además un `PerfilEstudiante`.
- Token/JWT para Ionic se puede añadir en Phase 3 sin cambiar estas reglas.
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class HasStudentProfile(BasePermission):
    """Allow only authenticated users that already have PerfilEstudiante."""

    message = (
        "Se requiere un perfil de estudiante. "
        "/ A student profile is required."
    )

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # related_name en PerfilEstudiante.usuario → user.perfil_estudiante
        return hasattr(user, "perfil_estudiante")
