# application-management-api

A small REST API, built with [FastAPI](https://fastapi.tiangolo.com/) and MongoDB, for keeping a catalog of applications. Each application has a name, a URL, a description, images, and a history of changes. You can list, view, create and deactivate applications (deactivating is a soft delete).

## Tech stack

- Python 3.14
- FastAPI, served with `fastapi run` (Uvicorn)
- MongoDB through `pymongo`
- `pydantic-settings` to load configuration from environment variables / `.env`
- `pytest` + `mongomock` for tests, `ruff` for linting and formatting

## Project structure

```
app/
├── main.py                 # App factory: middleware, exception handlers, routers
├── api/v1/
│   ├── router.py           # Mounts the v1 routers under /api/v1
│   └── apps.py             # /apps endpoints (HTTP layer only)
├── core/
│   ├── config.py           # Settings (pydantic-settings)
│   └── exceptions.py       # Domain errors, mapped to HTTP status codes in main.py
├── db/mongodb.py           # MongoDB client and the get_collections dependency
├── schemas/app.py          # Pydantic request/response models
└── services/
    ├── app_service.py      # Business logic
    └── mappers.py          # MongoDB documents -> response models
tests/                      # pytest suite (MongoDB replaced by mongomock)
pyproject.toml              # Project metadata, pytest and ruff config
requirements.txt / requirements-dev.txt
Dockerfile
```

Requests flow `api` → `services` → `db`. Endpoints receive the MongoDB collections through FastAPI's dependency injection (`Depends(get_collections)`), so tests override that dependency instead of patching modules.

## Configuration

The service reads its settings from environment variables. For local development, copy `.env.example` to `.env` and adjust it (`.env` is already in `.gitignore`):

```dotenv
MONGODB_USERNAME=admin
MONGODB_PASSWORD=secret
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=app_management

MONGODB_COLLECTION=applications
MONGODB_COLLECTION_IMAGES=images
MONGODB_COLLECTION_CHANGES=changes
```

| Variable | Description |
| --- | --- |
| `MONGODB_USERNAME` / `MONGODB_PASSWORD` | MongoDB credentials (URL-encoded automatically) |
| `MONGODB_HOST` / `MONGODB_PORT` | MongoDB host and port (the client connects with `directConnection=true`) |
| `MONGODB_DATABASE` | Database name |
| `MONGODB_COLLECTION` | Collection that stores applications |
| `MONGODB_COLLECTION_IMAGES` | Collection that stores application images |
| `MONGODB_COLLECTION_CHANGES` | Collection that stores the change history |

All of these are required. If one is missing, the first request that reaches MongoDB fails with a pydantic `ValidationError` that names the missing setting.

## Running locally

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env

fastapi dev app/main.py --port 4000   # auto-reload
# or
fastapi run app/main.py --port 4000
```

The API is then available at `http://localhost:4000/api/v1`.

## Tests and linting

```bash
pytest
ruff check .
ruff format .
```

The tests use `mongomock`, so they do not need a running MongoDB.

## Running with Docker

```bash
docker build -t application-management-api .
docker run --rm -p 4000:4000 --env-file .env application-management-api
```

If MongoDB runs on your host machine, set `MONGODB_HOST=host.docker.internal` (Docker Desktop) so the container can reach it.

## API

Every route is under `/api/v1`. The interactive docs (`/docs`, `/redoc`, `/openapi.json`) are turned off on purpose.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/apps?status=ACTIVE\|INACTIVE` | List applications filtered by status (defaults to `ACTIVE`) |
| `GET` | `/apps/{app_id}/details` | Get one application with its images and change history |
| `POST` | `/app/new` | Create an application (and its images) |
| `PUT` | `/apps/{app_id}` | Deactivate an application (soft delete) |

### List applications

```bash
curl "http://localhost:4000/api/v1/apps?status=ACTIVE"
```

```json
{
  "data": [
    { "_id": "665f...", "url": "https://example.com", "name": "Example", "description": "Demo app" }
  ]
}
```

### Get application details

```bash
curl http://localhost:4000/api/v1/apps/665f.../details
```

```json
{
  "data": {
    "_id": "665f...",
    "url": "https://example.com",
    "name": "Example",
    "description": "Demo app",
    "images": [
      { "_id": "6660...", "applicationId": "665f...", "url": "https://example.com/logo.png", "type": "logo" }
    ],
    "active": true,
    "changes": [
      { "_id": "6661...", "applicationId": "665f...", "changeType": "new", "datetime": "2026-10-18 12:00:00", "description": "add new App Example" }
    ]
  }
}
```

### Create an application

```bash
curl -X POST http://localhost:4000/api/v1/app/new \
  -H "Content-Type: application/json" \
  -d '{
        "data": {
          "url": "https://example.com",
          "name": "Example",
          "description": "Demo app",
          "images": [{ "url": "https://example.com/logo.png", "type": "logo" }]
        }
      }'
```

```json
{ "statusCode": "Ok", "_id": "665f..." }
```

The service saves the application with `active: true`, saves each image in the images collection, and records a `new` entry in the changes collection.

### Deactivate an application

```bash
curl -X PUT http://localhost:4000/api/v1/apps/665f...
```

```json
{ "app_id": "665f...", "message": "App deleted successfully." }
```

Nothing is removed from the database. The service sets `active` to `false` and records a `delete` entry in the changes collection.

### Errors

Errors come back in FastAPI's standard format, `{ "detail": "<message>" }`:

| Status | Detail | When |
| --- | --- | --- |
| `400` | `Invalid ID format` | `app_id` is not a valid MongoDB ObjectId |
| `404` | `Application not found` | No application has that `app_id` |
| `202` | `Application is already inactive` | On deactivate, the application is already inactive |
| `422` | Validation error | The request body or query parameters are invalid |

## Data model

The API uses three MongoDB collections:

- **applications**: `url`, `name`, `description`, `active`, `images` (image ids), `changes` (change ids)
- **images**: `applicationId`, `url`, `type`, `datetime`
- **changes**: `applicationId`, `changeType` (`new` / `delete`), `datetime`, `description`
