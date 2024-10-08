# A multi-stage build docker file
# https://docs.docker.com/build/building/multi-stage/
#
# the first) stage is used to build the application
# the main advantage is, that NO build-tools need to be available locally
# everything is done "inside" the image
#
# there are a couple of images available: https://hub.docker.com/_/python/

FROM python:3.11-bookworm as builder

# define a place where the output of the build is put
WORKDIR /app

# we setup poetry in debian

RUN pip install poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# use the project to the working directory
COPY pyproject.toml poetry.lock ./

# the mysql client for python needs some development-libraries
# this is a very good example why a multi-stage docker file is better for building
# see this comment from the python mysql client:
# 'Building mysqlclient on Windows is very hard. But there are some binary wheels you can install easily....'
RUN apt-get update && apt-get install -y python3-dev default-libmysqlclient-dev build-essential pkg-config
RUN poetry add mysqlclient
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# ---------------------------------------------------------------------------
# the second) stage is used for runtime/production
# we have now a different base-image which is smaller for production
FROM python:3.11-slim-bookworm

WORKDIR /opt/django-demo

# provide a DJANGO admin user and point to the specific production settings file
ENV DJANGO_SUPERUSER_PASSWORD=admin \
    DJANGO_SETTINGS_MODULE=swd_django_demo.settings_prod \
    PATH="/opt/django-demo/.venv/bin:$PATH"

# still we needs some additional stuff
# we need mariadb library (very, very similar to mysql) to access the db
# this is the runtime library dependency of mysqlclient
RUN apt-get update && apt-get install -y libmariadb3

# copy the poetry created python environment to the runtime image
COPY --from=builder /app/.venv /opt/django-demo/.venv

# it is a best practise to create a seperate user and not execute everything with root
RUN useradd -d /opt/django-demo django-demo-user
USER django-demo-user

# copy our project to the application directory
COPY --chown=django-demo-user . /opt/django-demo

ENTRYPOINT ["/opt/django-demo/entrypoint.sh"]