"""
Tests de la API Phase 2: filtros por grado/categoría y scoring en servidor.

APITestCase = TestCase + cliente DRF (auth helpers, JSON).
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import PerfilEstudiante
from trivia.choices import GradoEscolar
from trivia.models import Categoria, OpcionRespuesta, Pregunta
from trivia.scoring import PUNTOS_POR_ACIERTO

User = get_user_model()


class TriviaAPIFixtureMixin:
    """Helpers compartidos para armar datos de prueba."""

    def _make_student(self, username: str = "alumno", grado: str = GradoEscolar.PRIMERO_BASICO):
        user = User.objects.create_user(username=username, password="pass12345")
        perfil = PerfilEstudiante.objects.create(usuario=user, grado=grado)
        return user, perfil

    def _seed_questions(self):
        cat_mates = Categoria.objects.create(nombre="Matemáticas", descripcion="Números")
        cat_hist = Categoria.objects.create(nombre="Historia", descripcion="Chile")
        cat_off = Categoria.objects.create(nombre="Archivada", activa=False)

        q1 = Pregunta.objects.create(
            categoria=cat_mates,
            enunciado="¿Cuánto es 2+2?",
            grado=GradoEscolar.PRIMERO_BASICO,
            explicacion="2+2=4",
        )
        o_ok = OpcionRespuesta.objects.create(
            pregunta=q1, texto="4", es_correcta=True, orden=1
        )
        o_bad = OpcionRespuesta.objects.create(
            pregunta=q1, texto="5", es_correcta=False, orden=2
        )

        q2 = Pregunta.objects.create(
            categoria=cat_hist,
            enunciado="Capital de Chile?",
            grado=GradoEscolar.PRIMERO_BASICO,
            explicacion="Santiago",
        )
        OpcionRespuesta.objects.create(
            pregunta=q2, texto="Santiago", es_correcta=True, orden=1
        )
        OpcionRespuesta.objects.create(
            pregunta=q2, texto="Valparaíso", es_correcta=False, orden=2
        )

        q_medio = Pregunta.objects.create(
            categoria=cat_mates,
            enunciado="Derivada de x^2",
            grado=GradoEscolar.CUARTO_MEDIO,
            explicacion="2x",
        )
        OpcionRespuesta.objects.create(
            pregunta=q_medio, texto="2x", es_correcta=True, orden=1
        )

        q_inactive = Pregunta.objects.create(
            categoria=cat_mates,
            enunciado="Pregunta apagada",
            grado=GradoEscolar.PRIMERO_BASICO,
            activa=False,
        )
        OpcionRespuesta.objects.create(
            pregunta=q_inactive, texto="x", es_correcta=True, orden=1
        )

        Pregunta.objects.create(
            categoria=cat_off,
            enunciado="En categoría inactiva",
            grado=GradoEscolar.PRIMERO_BASICO,
        )

        return {
            "cat_mates": cat_mates,
            "cat_hist": cat_hist,
            "q1": q1,
            "o_ok": o_ok,
            "o_bad": o_bad,
            "q2": q2,
            "q_medio": q_medio,
            "q_inactive": q_inactive,
        }


class PreguntaFilterAPITests(TriviaAPIFixtureMixin, APITestCase):
    """Happy + error paths del listado filtrado."""

    def setUp(self):
        self.user, self.perfil = self._make_student()
        self.data = self._seed_questions()
        self.url = reverse("api-preguntas")

    def test_unauthenticated_rejected(self):
        # DRF may return 401 (Basic challenge) or 403 (no WWW-Authenticate).
        response = self.client.get(self.url, {"grado": "1B"})
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_missing_grado_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("grado", response.data)

    def test_invalid_grado_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {"grado": "99X"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("grado", response.data)

    def test_filter_by_grado_happy_path(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {"grado": "1B"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in response.data}
        self.assertIn(self.data["q1"].id, ids)
        self.assertIn(self.data["q2"].id, ids)
        self.assertNotIn(self.data["q_medio"].id, ids)
        self.assertNotIn(self.data["q_inactive"].id, ids)

    def test_filter_by_grado_and_categoria(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            self.url,
            {"grado": "1B", "categoria": self.data["cat_mates"].id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in response.data}
        self.assertEqual(ids, {self.data["q1"].id})

    def test_options_never_expose_es_correcta(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {"grado": "1B"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for pregunta in response.data:
            for opcion in pregunta["opciones"]:
                self.assertNotIn("es_correcta", opcion)
                self.assertIn("id", opcion)
                self.assertIn("texto", opcion)

    def test_categorias_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("api-categorias"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        nombres = {item["nombre"] for item in response.data}
        self.assertIn("Matemáticas", nombres)
        self.assertIn("Historia", nombres)
        self.assertNotIn("Archivada", nombres)


class RespuestaScoringAPITests(TriviaAPIFixtureMixin, APITestCase):
    """Happy + error paths del POST de respuesta y scoring server-side."""

    def setUp(self):
        self.user, self.perfil = self._make_student()
        self.data = self._seed_questions()
        self.url = reverse("api-respuestas")

    def test_unauthenticated_rejected(self):
        # DRF may return 401 (Basic challenge) or 403 (no WWW-Authenticate).
        response = self.client.post(
            self.url,
            {"pregunta": self.data["q1"].id, "opcion": self.data["o_ok"].id},
            format="json",
        )
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_user_without_profile_gets_403(self):
        bare = User.objects.create_user(username="sinperfil", password="pass12345")
        self.client.force_authenticate(user=bare)
        response = self.client.post(
            self.url,
            {"pregunta": self.data["q1"].id, "opcion": self.data["o_ok"].id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_correct_answer_awards_points_and_streak(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url,
            {"pregunta": self.data["q1"].id, "opcion": self.data["o_ok"].id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["correcta"])
        self.assertEqual(response.data["puntos_obtenidos"], PUNTOS_POR_ACIERTO)
        self.assertEqual(response.data["perfil"]["puntos"], PUNTOS_POR_ACIERTO)
        self.assertEqual(response.data["perfil"]["racha_actual"], 1)
        self.assertEqual(response.data["perfil"]["racha_maxima"], 1)
        self.assertEqual(response.data["perfil"]["penalizaciones"], 0)
        self.assertEqual(response.data["explicacion"], "2+2=4")

        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.puntos, PUNTOS_POR_ACIERTO)
        self.assertEqual(self.perfil.racha_actual, 1)

    def test_incorrect_answer_penalizes_and_resets_streak(self):
        self.perfil.puntos = 30
        self.perfil.racha_actual = 3
        self.perfil.racha_maxima = 5
        self.perfil.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url,
            {"pregunta": self.data["q1"].id, "opcion": self.data["o_bad"].id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["correcta"])
        self.assertEqual(response.data["puntos_obtenidos"], 0)
        self.assertEqual(response.data["perfil"]["puntos"], 30)  # no resta puntos
        self.assertEqual(response.data["perfil"]["penalizaciones"], 1)
        self.assertEqual(response.data["perfil"]["racha_actual"], 0)
        self.assertEqual(response.data["perfil"]["racha_maxima"], 5)  # se conserva

        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.penalizaciones, 1)
        self.assertEqual(self.perfil.racha_actual, 0)
        self.assertEqual(self.perfil.racha_maxima, 5)

    def test_client_cannot_inject_points_or_correct_flag(self):
        """Extra keys from the client must be ignored; DB decides correctness."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url,
            {
                "pregunta": self.data["q1"].id,
                "opcion": self.data["o_bad"].id,
                "correcta": True,
                "puntos": 9999,
                "puntos_obtenidos": 9999,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["correcta"])
        self.assertEqual(response.data["puntos_obtenidos"], 0)
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.puntos, 0)
        self.assertEqual(self.perfil.penalizaciones, 1)

    def test_option_from_other_question_returns_400(self):
        self.client.force_authenticate(user=self.user)
        other_ok = self.data["q2"].opciones.filter(es_correcta=True).first()
        response = self.client.post(
            self.url,
            {"pregunta": self.data["q1"].id, "opcion": other_ok.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("opcion", response.data)
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.puntos, 0)

    def test_inactive_question_rejected(self):
        self.client.force_authenticate(user=self.user)
        inactive_opt = self.data["q_inactive"].opciones.first()
        response = self.client.post(
            self.url,
            {"pregunta": self.data["q_inactive"].id, "opcion": inactive_opt.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_streak_updates_max_on_consecutive_correct(self):
        self.client.force_authenticate(user=self.user)
        q2_ok = self.data["q2"].opciones.filter(es_correcta=True).first()

        r1 = self.client.post(
            self.url,
            {"pregunta": self.data["q1"].id, "opcion": self.data["o_ok"].id},
            format="json",
        )
        r2 = self.client.post(
            self.url,
            {"pregunta": self.data["q2"].id, "opcion": q2_ok.id},
            format="json",
        )
        self.assertEqual(r1.status_code, status.HTTP_200_OK)
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertEqual(r2.data["perfil"]["racha_actual"], 2)
        self.assertEqual(r2.data["perfil"]["racha_maxima"], 2)
        self.assertEqual(r2.data["perfil"]["puntos"], PUNTOS_POR_ACIERTO * 2)

    def test_perfil_me_endpoint(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("api-perfil"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "alumno")
        self.assertEqual(response.data["grado"], GradoEscolar.PRIMERO_BASICO)
        self.assertEqual(response.data["puntos"], 0)
