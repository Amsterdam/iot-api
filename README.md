# iot #


### Install procedure ###

```
git clone Full git address of the repository (eq. https://github.com/Amsterdam/example.git) iot
cd iot
```

Start the docker containers manually
```
docker-compose up -d
```

#### Local development ####

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
