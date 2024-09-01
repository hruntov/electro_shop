#!/bin/bash

cd myshop && \
python manage.py migrate
python manage.py loaddata shop/fixtures/shop.json
python manage.py loaddata myshop/fixtures/users.json
python manage.py clearcache | python manage.py shell
python manage.py collectstatic --noinput
celery -A myshop worker -l info &
celery -A myshop flower --port=5555 &
python manage.py livereload --host=0.0.0.0 --port=35729 &
python manage.py runserver 0.0.0.0:8000
