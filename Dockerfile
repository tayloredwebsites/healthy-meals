
# Use the docker container with UV built into it.
# First, build the application in the `/app` directory.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# ARG IS_PROD
ARG SASS_VERSION=1.85.0
ARG SASS_URL="https://github.com/sass/dart-sass/releases/download/${SASS_VERSION}/dart-sass-${SASS_VERSION}-linux-x64.tar.gz"

# Install curl and Dart Sass
RUN apt-get update && apt-get install -y curl \
    && curl -OL $SASS_URL \
    && tar -xzf dart-sass-${SASS_VERSION}-linux-x64.tar.gz \
    && rm -rf dart-sass-${SASS_VERSION}-linux-x64.tar.gz
# add dart-sass directory (with sass command) to path
ENV PATH=$PATH:./dart-sass


# #######################################################################################################################
# # Then, use a final image without uv and dart
# FROM python:3.12-slim-bookworm

# # Copy the application from the builder
# COPY --from=builder --chown=app:app /app /app

# WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Expose port 8000
EXPOSE 8000

# Use gunicorn on port 8000
CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "healthy_meals.wsgi:application"]
