#!/bin/sh

python manage.py migrate --noinput

exec gunicorn --bind 0.0.0.0:8080 config.wsgi:application
