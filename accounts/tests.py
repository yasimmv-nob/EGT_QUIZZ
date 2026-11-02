"""
Tests de `accounts`.

La lógica de scoring vive en `trivia.scoring` / `trivia.tests` (Phase 2).
Aquí solo smoke del modelo de perfil.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import PerfilEstudiante
from trivia.choices import GradoEscolar

User = get_user_model()


class PerfilEstudianteModelTests(TestCase):
    def test_str_includes_username_and_points(self):
        user = User.objects.create_user(username="ana", password="pass12345")
        perfil = PerfilEstudiante.objects.create(
            usuario=user,
            grado=GradoEscolar.SEGUNDO_BASICO,
            puntos=15,
        )
        text = str(perfil)
        self.assertIn("ana", text)
        self.assertIn("15", text)
