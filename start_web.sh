#!/bin/bash

cd myshop && \
python manage.py migrate
python manage.py clearcache | python manage.py shell
celery -A myshop worker -l info &
python manage.py runserver 0.0.0.0:8000
