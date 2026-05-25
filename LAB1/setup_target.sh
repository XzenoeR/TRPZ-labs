#!/bin/bash

set -e

echo "Оновлення системи..."
sudo apt-get update && sudo apt-get upgrade -y

echo "Встановлення Nginx..."
sudo apt-get install -y nginx

echo "Встановлення Docker та Docker Compose..."
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "Додавання поточного користувача до групи docker..."
sudo usermod -aG docker $USER

echo "Створення директорії для проєкту..."
sudo mkdir -p /opt/mywebapp
sudo chown -R $USER:$USER /opt/mywebapp

echo "Налаштування завершено успішно!"