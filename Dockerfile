# Pull base image and give it an alias 'python_base'
FROM docker.io/python:3.12.9-slim-bullseye AS python_base

# To Do: figure out how to put migrations and compilation into a separate stage
#  - https://docs.docker.com/build/building/multi-stage/
#  - to build stage to minimize setup time

# # Install apt packages
# RUN apt-get -y update \
#   && apt-get install --no-install-recommends -y \
#   # dependencies for building Python packages
#   build-essential \
#   # psycopg dependencies
#   libpq-dev \
#   # Translations dependencies
#   gettext \
#   # curl to get dart-sass
#   curl \
#   # cleaning up unused files
#   && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
#   && rm -rf /var/lib/apt/lists/*

# # # Install dependencies
# # RUN pdm install -G test
# COPY pyproject.toml /tmp/pyproject.toml
# RUN set -ex && \
#     pip install --upgrade pip && \
#     pip install -r /tmp/requirements.txt && \
#     rm -rf /root/.cache/


# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# # Create and set work directory called `code`
# RUN mkdir -p /code
# WORKDIR /code

# ARG CURL
# RUN set -ex && \
#     # download curl
#     # Install cURL
#     apt-get update && apt-get install -y curl && \
#     # download pdm using sha checksum check && \
#     curl -sSLO https://pdm-project.org/install-pdm.py && \
#     curl -sSL https://pdm-project.org/install-pdm.py.sha256 | shasum -a 256 -c - && \
#     # Run the installer \
#     python3 install-pdm.py
#     # pip install -r /tmp/requirements.txt && \
#     # rm -rf /root/.cache/



ARG IS_PROD
ARG SASS_VERSION=1.85.0
ARG SASS_URL="https://github.com/sass/dart-sass/releases/download/${SASS_VERSION}/dart-sass-${SASS_VERSION}-linux-x64.tar.gz"

ENV IS_PROD=${IS_PROD} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=2.1.3

# System dependencies (as well as poetry):
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
    bash \
    build-essential \
    curl \
    gettext \
    git \
    libpq-dev \
    wget \
  # Cleaning cache:
  && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* \
  && pip install "poetry==$POETRY_VERSION" && poetry --version

  # Install Dart Sass
RUN apt-get update && apt-get install -y \
    curl \
    && curl -OL $SASS_URL \
    && tar -xzf dart-sass-${SASS_VERSION}-linux-x64.tar.gz \
    && rm -rf dart-sass-${SASS_VERSION}-linux-x64.tar.gz


# # DART SASS
# RUN curl -OL $SASS_URL
# # download dart-sass and add to PATH
# # Extract the release
# RUN tar -xzf dart-sass-${SASS_VERSION}-linux-x64.tar.gz
# # Clean up downloaded files (optional)
# RUN rm -rf dart-sass-${SASS_VERSION}-linux-x64.tar.gz

# add dart-sass directory (with sass command) to path
ENV PATH=$PATH:./dart-sass

# # POETRY
# RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy only requirements to cache them in docker layer
WORKDIR /code
# COPY poetry.lock pyproject.toml /code/

# Creating folders, and files for a project:
COPY . /code

# Project requirements initialization using poetry:
# RUN poetry install $(test "$IS_PROD" == production && echo "--only=main") --no-interaction --no-ansi
# RUN poetry install --no-interaction --no-ansi && echo "poetry install is completed!"
RUN poetry install && echo "poetry install is completed!"

# Creating folders, and files for a project:
COPY . /code
