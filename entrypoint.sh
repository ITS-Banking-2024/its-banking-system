#!/bin/sh

## initial database migration
## in a production environment this would typicalle not be put here. the database would be maintained seperately 
python /opt/django-demo/manage.py migrate
python /opt/django-demo/manage.py createsuperuser --noinput --username admin --email admin@localhost

## it is important to listen on 0.0.0.0 in the container to map this address to a local port
python /opt/django-demo/manage.py runserver 0.0.0.0:8000