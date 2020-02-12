FROM amsterdam/python
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN mkdir -p /app && chown datapunt /app
RUN mkdir -p /static && chown datapunt /static
RUN mkdir -p /deploy && chown datapunt /deploy

COPY src /app/
COPY deploy /deploy/
COPY requirements.txt /
COPY requirements /requirements/

WORKDIR /app

RUN pip install -r /requirements.txt
RUN pip install -r /requirements/req-test.txt

USER datapunt

ARG SECRET_KEY=x
ARG OIDC_RP_CLIENT_ID=x
ARG OIDC_RP_CLIENT_SECRET=x
ARG AMSTERDAM_PRIVACY_MAP_EMAIL_ADDRESS=x
RUN python manage.py collectstatic --no-input

CMD uwsgi