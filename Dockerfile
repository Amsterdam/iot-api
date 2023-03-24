FROM python:3.11 as app

RUN apt-get update \
  && apt-get autoremove -y \
  && apt-get install --no-install-recommends -y \
  postgresql-client-13 \
  gdal-bin \
  libgdal-dev \
  netcat \
  && rm -rf /var/lib/apt/lists/* /var/cache/debconf/*-old \
  && pip install --upgrade pip \
  && useradd --user-group -m app

WORKDIR /app/install
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt && pip cache purge

COPY deploy /app/deploy

WORKDIR /app/src
COPY src .
COPY pyproject.toml /app

ARG SECRET_KEY=not-used
ARG OIDC_RP_CLIENT_ID=not-used
ARG OIDC_RP_CLIENT_SECRET=not-used
RUN DATABASE_ENABLED=false python manage.py collectstatic --no-input

RUN mkdir /home/app/.azure
RUN chown app:app /home/app/.azure
USER app

CMD ["/app/deploy/docker-run.sh"]

# stage 2, dev
FROM app as dev

USER root
WORKDIR /app/install
ADD requirements_dev.txt requirements_dev.txt
RUN pip install -r requirements_dev.txt && pip cache purge

WORKDIR /app/src
USER app

# CMD ["./manage.py", "runserver", "0.0.0.0:8000"]
CMD ["/app/deploy/docker-run.sh"]

# stage 3, tests
FROM dev as tests

WORKDIR /app/tests
ADD tests .

# ENV COVERAGE_FILE=/home/runner/.coverage
ENV PYTHONPATH=/app/src

CMD ["pytest"]
