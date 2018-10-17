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

RUN pip install --no-cache-dir -r /requirements.txt
RUN pip install --no-cache-dir -r /requirements/req-test.txt

USER datapunt

RUN export SECRET_KEY=insecure
RUN export DJANGO_SETTINGS_MODULE=iot.settings.development

RUN python manage.py collectstatic --no-input

CMD uwsgi