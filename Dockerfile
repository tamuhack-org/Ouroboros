FROM python:3.13

# currently pinned to uv 0.9, new members will have to update
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Install the project's dependencies using the lockfile and settings
COPY pyproject.toml uv.lock ./

# Step 1: Sync dependencies (No cache mounts)
RUN uv sync --frozen --no-install-project --no-dev

ADD . /app

# Step 2: Sync the project itself (No cache mounts)
RUN uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR "hiss"

RUN python manage.py collectstatic --no-input

ARG DATABASE_URL

# NOTE: Running migrations during the build process is risky (see notes below)
RUN python manage.py migrate

ENTRYPOINT []

CMD ["gunicorn", "-b", "0.0.0.0:8000", "hiss.wsgi:application"]
