FROM python:3.11 as base

RUN apt-get update \
  && apt-get autoremove -y \
  && apt-get install --no-install-recommends -y \
  postgresql-client-13 \
  gdal-bin \
  libgdal-dev \
  && rm -rf /var/lib/apt/lists/* /var/cache/debconf/*-old \
  && pip install --upgrade pip \
  && useradd --user-group -m app

WORKDIR /app/install
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt && pip cache purge

COPY deploy /app/deploy

ARG SECRET_KEY=not-used
ARG OIDC_RP_CLIENT_ID=not-used
ARG OIDC_RP_CLIENT_SECRET=not-used
# RUN DATABASE_ENABLED=false python manage.py collectstatic --no-input

RUN mkdir /home/app/.azure
RUN chown app:app /home/app/.azure

WORKDIR /app/src
ONBUILD COPY src .
ONBUILD COPY pyproject.toml /app
ONBUILD RUN DATABASE_ENABLED=false python manage.py collectstatic --no-input
ONBUILD RUN chown -R app:app /app /static
ONBUILD USER app

CMD ["/app/deploy/docker-run.sh"]

# stage 2, dev
FROM base as app

# stage 2, dev
FROM base as dev

USER root
RUN apt-get update \
  && apt-get autoremove -y \
  && apt-get install --no-install-recommends -y \
  netcat \
  && rm -rf /var/lib/apt/lists/* /var/cache/debconf/*-old

WORKDIR /app/install
ADD requirements_dev.txt requirements_dev.txt
RUN pip install -r requirements_dev.txt && pip cache purge

# stage 3, tests
FROM dev as tests

WORKDIR /app/tests
ADD tests .

# ENV COVERAGE_FILE=/home/runner/.coverage
ENV PYTHONPATH=/app/src

CMD ["pytest"]
