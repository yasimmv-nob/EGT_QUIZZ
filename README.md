# EGT_QUIZZ

Gamified educational trivia for the Chilean school curriculum (1° básico → 4° medio).

**Stack (Phase 1):** Python 3.12+, Django 5.x, Django REST Framework, SQLite (local).

Phase 1 delivers the data models and Django Admin for content editing. The DRF answer-scoring API is Phase 2; Ionic is Phase 3.

## Project layout

```
config/          # Django project settings / URLs
trivia/          # Categoria, Pregunta, OpcionRespuesta
accounts/        # PerfilEstudiante (points, penalties, streaks)
manage.py
requirements.txt
```

## Setup (local)

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open:

- Admin: http://127.0.0.1:8000/admin/

## Models (Phase 1)

| Model | App | Purpose |
| --- | --- | --- |
| `Categoria` | `trivia` | Subject / topic grouping |
| `Pregunta` | `trivia` | Question text + Chilean `grado` filter |
| `OpcionRespuesta` | `trivia` | Answer choices (`es_correcta`) |
| `PerfilEstudiante` | `accounts` | Points, penalties, current/max streaks, grade |

`grado` uses Chilean levels: 1°–8° básico and 1°–4° medio.

## Roadmap

1. **Phase 1 (this PR):** Django models + Admin
2. **Phase 2:** DRF list/filter + POST answers with server-side scoring
3. **Phase 3:** Ionic (Angular) client
4. **Phase 4:** Capacitor packaging + cloud host
