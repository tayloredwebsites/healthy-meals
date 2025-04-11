# Pull base image and give it an alias 'python_base'
FROM docker.io/python:3.12.9-slim-bullseye AS python_base

# To Do: figure out how to put migrations and compilation into a separate stage
#  - https://docs.docker.com/build/building/multi-stage/
#  - to build stage to minimize setup time

# Install apt packages
RUN apt-get -y update \
  && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # curl to get dart-sass
  curl \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# # Install dependencies
RUN pdm install -G test
# COPY requirements.txt /tmp/requirements.txt
# RUN set -ex && \
#     pip install --upgrade pip && \
#     pip install -r /tmp/requirements.txt && \
#     rm -rf /root/.cache/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set work directory called `code`
RUN mkdir -p /code
WORKDIR /code

# download dart-sass and add to PATH
ARG SASS_VERSION=1.85.0
ARG SASS_URL="https://github.com/sass/dart-sass/releases/download/${SASS_VERSION}/dart-sass-${SASS_VERSION}-linux-x64.tar.gz"
RUN curl -OL $SASS_URL
# Extract the release
RUN tar -xzf dart-sass-${SASS_VERSION}-linux-x64.tar.gz
# Clean up downloaded files (optional)
RUN rm -rf dart-sass-${SASS_VERSION}-linux-x64.tar.gz
ENV PATH=$PATH:./dart-sass

# Copy local server code
COPY . /code
