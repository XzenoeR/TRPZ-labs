#!/bin/bash
set -e

echo "=== Початок розгортання Notes Service ==="

echo "[1/8] Встановлення пакетів..."
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3-venv python3-pip mariadb-server nginx libmariadb3 libmariadb-dev gcc

echo "[2/8] Створення користувачів системи..."
for u in student teacher; do
    if ! id "$u" &>/dev/null; then
        useradd -m -s /bin/bash "$u"
        echo "$u:12345678" | chpasswd
        chage -d 0 "$u"
        usermod -aG sudo "$u"
    fi
done

if ! id "operator" &>/dev/null; then
    useradd -m -s /bin/bash operator
    echo "operator:12345678" | chpasswd
    chage -d 0 operator
fi

echo "operator ALL=(ALL) NOPASSWD: /usr/bin/systemctl start mywebapp.service, /usr/bin/systemctl stop mywebapp.service, /usr/bin/systemctl restart mywebapp.service, /usr/bin/systemctl status mywebapp.service, /usr/bin/systemctl start mywebapp.socket, /usr/bin/systemctl stop mywebapp.socket, /usr/bin/systemctl restart mywebapp.socket, /usr/bin/systemctl status mywebapp.socket, /usr/bin/systemctl reload nginx" > /etc/sudoers.d/operator
chmod 440 /etc/sudoers.d/operator

if ! id "mywebapp" &>/dev/null; then
    useradd -r -s /bin/false mywebapp
fi

echo "[3/8] Налаштування MariaDB..."
mysql -u root -e "CREATE DATABASE IF NOT EXISTS mywebapp;"
mysql -u root -e "CREATE USER IF NOT EXISTS 'app_user'@'127.0.0.1' IDENTIFIED BY 'app_password';"
mysql -u root -e "GRANT ALL PRIVILEGES ON mywebapp.* TO 'app_user'@'127.0.0.1';"
mysql -u root -e "FLUSH PRIVILEGES;"

echo "[4/8] Копіювання коду та налаштування Python..."
mkdir -p /opt/mywebapp

cp ./app.py /opt/mywebapp/
cp ./migrate.py /opt/mywebapp/

chown -R mywebapp:mywebapp /opt/mywebapp
cd /opt/mywebapp
python3 -m venv venv
/opt/mywebapp/venv/bin/pip install Flask mariadb Werkzeug
chown -R mywebapp:mywebapp /opt/mywebapp

echo "[5/8] Створення systemd-юнітів (Socket Activation + Migration)..."

cat << 'EOF' > /etc/systemd/system/mywebapp.socket
[Unit]
Description=Notes Service Socket

[Socket]
ListenStream=127.0.0.1:5000

[Install]
WantedBy=sockets.target
EOF

cat << 'EOF' > /etc/systemd/system/mywebapp.service
[Unit]
Description=Notes Service Web Application
After=network.target mariadb.service
Requires=mywebapp.socket

[Service]
User=mywebapp
Group=mywebapp
WorkingDirectory=/opt/mywebapp
ExecStartPre=/opt/mywebapp/venv/bin/python migrate.py --db-host 127.0.0.1 --db-port 3306 --db-user app_user --db-pass app_password --db-name mywebapp
ExecStart=/opt/mywebapp/venv/bin/python app.py --db-host 127.0.0.1 --db-port 3306 --db-user app_user --db-pass app_password --db-name mywebapp --app-port 5000
Restart=on-failure
EOF

systemctl daemon-reload
systemctl enable --now mywebapp.socket
systemctl stop mywebapp.service || true

echo "[6/8] Конфігурація Nginx..."
rm -f /etc/nginx/sites-enabled/default

cat << 'EOF' > /etc/nginx/sites-available/mywebapp
server {
    listen 80;
    server_name _;

    access_log /var/log/nginx/mywebapp_access.log;
    error_log /var/log/nginx/mywebapp_error.log;

    # Expose root and notes logic endpoints
    location = / { proxy_pass http://127.0.0.1:5000; }
    location /notes { proxy_pass http://127.0.0.1:5000; }

    # Explicitly block access to any health routes from public
    location /health { return 404; }
    location / { return 404; }
}
EOF

ln -sf /etc/nginx/sites-available/mywebapp /etc/nginx/sites-enabled/
systemctl restart nginx

echo "[7/8] Створення gradebook..."
echo "24" > /home/student/gradebook
chown student:student /home/student/gradebook
chmod 644 /home/student/gradebook

echo "[8/8] Блокування дефолтного користувача..."
DEFAULT_USER=$(logname || echo $SUDO_USER)
if [ -n "$DEFAULT_USER" ] && [ "$DEFAULT_USER" != "root" ]; then
    usermod -L "$DEFAULT_USER"
    echo "Користувача $DEFAULT_USER заблоковано."
else
    echo "Не вдалося визначити дефолтного користувача для блокування."
fi

echo "=== Розгортання успішно завершено! ==="
