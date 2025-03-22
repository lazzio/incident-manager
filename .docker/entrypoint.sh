#!/bin/sh

if [ "${RUN_MIGRATIONS}" = "true" ]; then
    echo ">>> Running migrations"
    python manage.py makemigrations
    python manage.py migrate
fi

if [ "${COLLECT_STATIC}" = "true" ]; then
    echo ">>> Collecting static files"
    python manage.py collectstatic --noinput
fi

# Create superuser
# 1. Check if the superuser already exists
# 2. If not, create the superuser
echo ">>> Checking if superuser exists"
echo "from django.contrib.auth.models import User; print(User.objects.filter(username='$ADMIN_USERNAME').exists())" | python manage.py shell

if [ $? -eq 0 ]; then
    echo ">>> Superuser already exists"
else
    echo ">>> Superuser does not exist"
    echo ">>> Creating superuser"
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')" | python manage.py shell
fi

echo ">>> Compiling i18n messages"
django-admin makemessages -l en -l fr -l es && django-admin compilemessages

echo ">>> Starting server"
gunicorn --bind 0.0.0.0:8000 --workers 2 incident_manager.wsgi:application