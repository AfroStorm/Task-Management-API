#!/bin/sh
# entrypoint.sh

# Generate a Django secret key
SECRET_KEY=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 50 ; echo '')

# Introduce a 5-second delay
sleep 3

# Replace the secret key in the settings.py with the generated one
sed -i "s|SECRET_KEY =.*|SECRET_KEY = '$SECRET_KEY'|" app/settings.py

# Introduce a 5-second delay
sleep 3

# Start Django server
python manage.py runserver 0.0.0.0:8000

# Continue with the original entrypoint logic
exec "$@"
