# EGT_QUIZZ

Gamified educational trivia for the Chilean school curriculum (1° básico → 4° medio).

**Stack:** Python 3.12+, Django 5.x, Django REST Framework, SQLite (local).

Phase 1 delivered models + Django Admin. **Phase 2** adds the DRF API with **server-side scoring**. Ionic is Phase 3.

## Project layout

```
config/          # Django project settings / URLs
trivia/          # Categoria, Pregunta, OpcionRespuesta + API / scoring
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
- API root examples below under `/api/`

```bash
python manage.py test
```

## Models

| Model | App | Purpose |
| --- | --- | --- |
| `Categoria` | `trivia` | Subject / topic grouping |
| `Pregunta` | `trivia` | Question text + Chilean `grado` filter |
| `OpcionRespuesta` | `trivia` | Answer choices (`es_correcta` — server only) |
| `PerfilEstudiante` | `accounts` | Points, penalties, current/max streaks, grade |

`grado` codes: `1B`…`8B` (básico), `1M`…`4M` (medio).

## API (Phase 2)

Base path: `/api/`. All endpoints require authentication.

### Auth assumptions

| Rule | Detail |
| --- | --- |
| Default permission | `IsAuthenticated` |
| Auth classes | Session (browsable API / cookies) + HTTP Basic (dev/curl) |
| Student profile | `POST /api/respuestas/` and `GET /api/perfil/` also require a linked `PerfilEstudiante` |
| Anti-cheat | Clients send only `pregunta` + `opcion` IDs. Correctness and points are computed on the server from `OpcionRespuesta.es_correcta`. List serializers never expose `es_correcta`. |
| Ionic (Phase 3) | Add Token/JWT later without changing these permission rules |

Create a student in Admin: User + inline **PerfilEstudiante** (grade + counters).

### Scoring rules (server)

| Event | Effect |
| --- | --- |
| Correct | `+10` puntos, `racha_actual += 1`, update `racha_maxima` if needed |
| Incorrect | `penalizaciones += 1`, `racha_actual = 0` (points are not decreased) |

Constant: `trivia.scoring.PUNTOS_POR_ACIERTO = 10`.

### Endpoints

#### `GET /api/categorias/`

Active categories for filters.

```bash
curl -u alumno:pass12345 http://127.0.0.1:8000/api/categorias/
```

#### `GET /api/preguntas/?grado=1B&categoria=<id>`

- `grado` **required** (`1B`…`4M`)
- `categoria` optional (category id)

```bash
# All active 1° básico questions
curl -u alumno:pass12345 "http://127.0.0.1:8000/api/preguntas/?grado=1B"

# Filter by category id as well
curl -u alumno:pass12345 "http://127.0.0.1:8000/api/preguntas/?grado=1B&categoria=1"
```

Example item (options omit `es_correcta`):

```json
{
  "id": 1,
  "enunciado": "¿Cuánto es 2+2?",
  "grado": "1B",
  "grado_display": "1° básico",
  "categoria": {"id": 1, "nombre": "Matemáticas", "descripcion": "..."},
  "opciones": [
    {"id": 10, "texto": "4", "orden": 1},
    {"id": 11, "texto": "5", "orden": 2}
  ]
}
```

#### `GET /api/preguntas/<id>/`

Single active question with public options.

#### `POST /api/respuestas/`

Body (only IDs — extra keys like `puntos` / `correcta` are ignored):

```json
{"pregunta": 1, "opcion": 10}
```

```bash
curl -u alumno:pass12345 \
  -H "Content-Type: application/json" \
  -d '{"pregunta": 1, "opcion": 10}' \
  http://127.0.0.1:8000/api/respuestas/
```

Example response:

```json
{
  "correcta": true,
  "puntos_obtenidos": 10,
  "puntos_por_acierto": 10,
  "explicacion": "2+2=4",
  "perfil": {
    "id": 1,
    "username": "alumno",
    "grado": "1B",
    "grado_display": "1° básico",
    "puntos": 10,
    "penalizaciones": 0,
    "racha_actual": 1,
    "racha_maxima": 1
  }
}
```

#### `GET /api/perfil/`

Current student's gamification counters.

```bash
curl -u alumno:pass12345 http://127.0.0.1:8000/api/perfil/
```

## Roadmap

1. **Phase 1:** Django models + Admin ✅
2. **Phase 2 (this PR):** DRF list/filter + POST answers with server-side scoring
3. **Phase 3:** Ionic (Angular) client
4. **Phase 4:** Capacitor packaging + cloud host
