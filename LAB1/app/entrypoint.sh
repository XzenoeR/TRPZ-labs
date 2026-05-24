#!/bin/bash
set -e

echo "Виконання міграції бази даних..."
python migrate.py --db-host db --db-port 3306 --db-user app_user --db-pass app_password --db-name mywebapp

echo "Запуск веб-сервера Flask..."
exec python app.py --db-host db --db-port 3306 --db-user app_user --db-pass app_password --db-name mywebapp --app-port 5000