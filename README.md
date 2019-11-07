# iot
This project serves the data for [slimmeapparaten.amsterdam.nl](https://slimmeapparaten.amsterdam.nl/) for which the 
frontend can be found over at [github.com/Amsterdam/register-slimme-apparaten-frontend](https://github.com/Amsterdam/).

### Note to reader
There is an import command in `management/commands/import_csv.py`, but that seems to not be run ever, at all? The data 
which is in the acceptance and production databases supposedly comes from a csv which arrived by email. That csv 
has however, been lost since. 


### How to run

Start the docker containers manually
```
docker-compose up
```

### Running tests

Also install test requirements
    
    pip install -r requirements/req-test.txt

and then run the tests

    python3 manage.py test

### Developing

While developing it's easiest to run the db in the container and django locally

    docker-compose up database
    python manage.py runserver
