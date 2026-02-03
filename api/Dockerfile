FROM ghcr.io/astral-sh/uv:debian
# Copy the project into the image
COPY . .

RUN apt-get update

# Disable development dependencies
ENV UV_NO_DEV=1

# Sync the project into a new environment, asserting the lockfile is up to date
RUN uv sync --locked

EXPOSE 8000

CMD ["uv", "run", "daphne", "-b", "0.0.0.0", "graph.asgi:application"]
