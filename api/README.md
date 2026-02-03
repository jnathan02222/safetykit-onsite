# Atlas backend

## Quickstart

The backend is managed with [uv](https://docs.astral.sh/uv/), which is a much better
package manager for Python, so begin by installing that.

uv automatically handles installation when you run a script, so there's no need to
make an install command.

Start the server with

```bash
uv run manage.py runserver
```

Make sure to define an `.env` file with

```
NEO4J_HOST=localhost
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DB=neo4j
```

This is necessary to connect the database. You can set up the [Neo4j](https://neo4j.com/)
database with [Docker](https://docs.docker.com/). Docker allows you containerize
various applications to make them easy to isolate and setup.

Then run

```bash
docker compose up
```

This creates a Neo4j container and a Docker volume to persist the data.

## Development

### File structure

```
frontend/
├── graph/          # Main API (currently all in urls.py)
├── integrations/   # Classes for grabbing data
├── wikipedia_api/  # Helper class for Wikipedia API
└── db.py           # Helper class to connect to Neo4j
```

### Tools

[ruff](https://docs.astral.sh/ruff/) is a Python formatter + linter.
Will probably be added as a CI check, but for now run it yourself.

[ty](https://docs.astral.sh/ty/) is a Python type checker. Types
should be used as often as possible.

Relevant backend technologies: [Django](https://www.djangoproject.com/),
[Django Ninja](https://django-ninja.dev/), [Neo4j](https://neo4j.com/)
and [Celery](https://docs.celeryq.dev/en/stable/) in the future
when integrations become scheduled.

### Deployment

To manually build the backend container, run

```bash
docker buildx build -t atlas-2-backend --platform linux/amd64,linux/arm64 .

docker tag atlas-2-backend jnathan02222/atlas-2-backend

docker push jnathan02222/atlas-2-backend
```
