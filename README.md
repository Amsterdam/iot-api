# iot
This project serves the data for [slimmeapparaten.amsterdam.nl](https://slimmeapparaten.amsterdam.nl/) for which the 
frontend can be found over at [github.com/Amsterdam/register-slimme-apparaten-frontend](https://github.com/Amsterdam/).

### Note to reader
There is am import command in `management/commands/import_csv.py`, but it is unclear where in Jenkins 
(or anywhere else) this command is run and what should be the data source. Can the future reader who 
is _"in the know"_ be so kind as to add that information to this readme?


### How to run

Start the docker containers manually
```
docker-compose up -d
```

#### Local development

To create the virtualenvironment (python3) and install requirements run:
```
make virtualenv
```

iot API
==================

This is a standard Django Rest Framework API.

```
docker-compose up database
python manage.py runserver
```
