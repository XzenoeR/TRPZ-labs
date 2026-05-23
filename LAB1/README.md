# Лабораторна робота №1 — Notes Service

## Варіант індивідуального завдання

**Номер студента:** N = 24

| Змінна | Формула      | Результат | Значення                                                            |
| ------ | ------------ | --------- | ------------------------------------------------------------------- |
| V2     | (24 % 2) + 1 | **1**     | Конфігурація через аргументи командного рядка; база даних — MariaDB |
| V3     | (24 % 3) + 1 | **1**     | Застосунок — Notes Service                                          |
| V5     | (24 % 5) + 1 | **5**     | Порт застосунку — 5000                                              |

### Опис індивідуального завдання

- **Застосунок:** Notes Service — простий сервіс для зберігання текстових нотаток
- **База даних:** MariaDB, підключення через `127.0.0.1:3306`
- **Конфігурація:** аргументи командного рядка
- **Порт застосунку:** `5000` (слухає на `127.0.0.1`)
- **Reverse proxy:** Nginx на порту `80`

---

## Структура репозиторію

```
.
├── app.py          # Веб-застосунок (Flask)
├── migrate.py      # Скрипт міграції бази даних
├── setup.sh        # Скрипт автоматичного розгортання
└── README.md
```

---

## Веб-застосунок

### Призначення

Notes Service — REST API сервіс для створення та перегляду текстових нотаток. Кожна нотатка містить поля: `id`, `title`, `content`, `created_at`.

### Архітектура системи

```
client → nginx (0.0.0.0:80) → app (127.0.0.1:5000) → MariaDB (127.0.0.1:3306)
```

Доступ до бази даних обмежений лише локально (`127.0.0.1`). Клієнти взаємодіють із системою виключно через nginx.

---

## API-ендпоінти

### Службові

| Метод | Ендпоінт        | Опис                                  | Відповідь                         |
| ----- | --------------- | ------------------------------------- | --------------------------------- |
| GET   | `/health/alive` | Перевірка живості сервісу             | `200 OK`                          |
| GET   | `/health/ready` | Перевірка готовності (з'єднання з БД) | `200 OK` або `500 + опис помилки` |

### Кореневий ендпоінт

| Метод | Ендпоінт | Опис                                                            |
| ----- | -------- | --------------------------------------------------------------- |
| GET   | `/`      | Повертає HTML-сторінку зі списком усіх ендпоінтів бізнес-логіки |

### Бізнес-логіка

| Метод | Ендпоінт      | Параметри          | Опис                                                          |
| ----- | ------------- | ------------------ | ------------------------------------------------------------- |
| GET   | `/notes`      | —                  | Список усіх нотаток (`id`, `title`)                           |
| POST  | `/notes`      | `title`, `content` | Створити нову нотатку                                         |
| GET   | `/notes/<id>` | —                  | Повний вміст нотатки (`id`, `title`, `created_at`, `content`) |

### Формат відповіді

Всі ендпоінти бізнес-логіки підтримують два формати відповіді залежно від заголовка `Accept`:

- `Accept: text/html` — повертає просту HTML-сторінку (без JS, без стилів; списки у вигляді таблиць)
- `Accept: application/json` — повертає дані у форматі JSON

**Приклади запитів:**

```bash
# Отримати список нотаток у JSON
curl -H "Accept: application/json" http://<VM_IP>/notes

# Отримати список нотаток у HTML
curl -H "Accept: text/html" http://<VM_IP>/notes

# Створити нотатку (JSON)
curl -X POST http://<VM_IP>/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Моя нотатка", "content": "Текст нотатки"}'

# Отримати нотатку за ID
curl -H "Accept: application/json" http://<VM_IP>/notes/1
```

---

## Налаштування середовища для розробки

### Вимоги

- Python 3.10+
- MariaDB (локально або у Docker)
- pip

### Локальний запуск

```bash
# 1. Клонувати репозиторій
git clone <URL репозиторію>
cd <назва репозиторію>

# 2. Створити віртуальне середовище
python3 -m venv venv
source venv/bin/activate

# 3. Встановити залежності
pip install Flask mariadb Werkzeug

# 4. Запустити міграцію БД
python migrate.py \
  --db-host 127.0.0.1 \
  --db-port 3306 \
  --db-user <user> \
  --db-pass <password> \
  --db-name mywebapp

# 5. Запустити застосунок
python app.py \
  --db-host 127.0.0.1 \
  --db-port 3306 \
  --db-user <user> \
  --db-pass <password> \
  --db-name mywebapp \
  --app-port 5000
```

Застосунок буде доступний за адресою `http://127.0.0.1:5000`.

---

## Розгортання

### Базовий образ віртуальної машини

Використовується офіційний образ **Ubuntu Server 24.04 LTS**:

- Завантажити: https://ubuntu.com/download/server
- Рекомендований образ: `ubuntu-24.04-live-server-amd64.iso`

### Вимоги до ресурсів ВМ

| Ресурс | Мінімум        | Рекомендовано                    |
| ------ | -------------- | -------------------------------- |
| CPU    | 1 vCPU         | 2 vCPU                           |
| RAM    | 1 GB           | 2 GB                             |
| Disk   | 10 GB          | 20 GB                            |
| Мережа | NAT або Bridge | Bridge (для зовнішнього доступу) |

### Спеціальні налаштування при встановленні OS

Спеціальних налаштувань не потрібно. Стандартна розбивка диску при встановленні Ubuntu Server є достатньою. При встановленні рекомендується:

- Вибрати мінімальну інсталяцію (без GUI)
- Увімкнути OpenSSH Server під час встановлення

### Вхід на ВМ

**SSH:**

```bash
ssh <default_user>@<VM_IP>
```

Credentials для дефолтного користувача задаються при встановленні Ubuntu. Після запуску `setup.sh` дефолтний користувач буде заблокований, і вхід можливий лише через:

| Користувач | Пароль за замовчуванням | Примітка                           |
| ---------- | ----------------------- | ---------------------------------- |
| `student`  | `12345678`              | Потрібно змінити при першому вході |
| `teacher`  | `12345678`              | Потрібно змінити при першому вході |
| `operator` | `12345678`              | Потрібно змінити при першому вході |

### Запуск автоматизації розгортання

```bash
# 1. Скопіювати файли на ВМ
scp app.py migrate.py setup.sh <default_user>@<VM_IP>:~/

# 2. Увійти на ВМ
ssh <default_user>@<VM_IP>

# 3. Зробити скрипт виконуваним і запустити з правами root
chmod +x setup.sh
sudo ./setup.sh
```

Після завершення скрипт виведе `=== Розгортання успішно завершено! ===`. Система готова до роботи.

### Що робить скрипт setup.sh

1. Встановлює пакети: `python3-venv`, `python3-pip`, `mariadb-server`, `nginx`, `libmariadb3`, `libmariadb-dev`, `gcc`
2. Створює системних користувачів: `student`, `teacher`, `operator`, `mywebapp`
3. Налаштовує MariaDB: створює БД `mywebapp` та користувача `app_user`
4. Копіює `app.py` та `migrate.py` у `/opt/mywebapp/`, встановлює Python-залежності у venv
5. Створює та активує systemd-юніти (`mywebapp.socket` + `mywebapp.service`) з socket activation
6. Налаштовує Nginx як reverse proxy
7. Створює файл `/home/student/gradebook` зі значенням `24`
8. Блокує дефолтного користувача системи (`usermod -L`)

### Systemd та Socket Activation

Застосунок запускається через systemd socket activation. Юніти:

- `/etc/systemd/system/mywebapp.socket` — слухає на `127.0.0.1:5000`
- `/etc/systemd/system/mywebapp.service` — запускає міграцію (`ExecStartPre`) та застосунок

```bash
# Перевірити статус
sudo systemctl status mywebapp.socket
sudo systemctl status mywebapp.service

# Перезапустити
sudo systemctl restart mywebapp.service
```

### Права користувача operator

Користувач `operator` може керувати сервісом та nginx без повних прав адміністратора:

```bash
sudo systemctl start mywebapp.service
sudo systemctl stop mywebapp.service
sudo systemctl restart mywebapp.service
sudo systemctl status mywebapp.service
sudo systemctl start mywebapp.socket
sudo systemctl stop mywebapp.socket
sudo systemctl restart mywebapp.socket
sudo systemctl status mywebapp.socket
sudo systemctl reload nginx
```

---

## Інструкція з тестування

### 1. Перевірка сервісів

```bash
# Перевірити, що socket і сервіс активні
systemctl status mywebapp.socket
systemctl status mywebapp.service

# Перевірити, що nginx запущений
systemctl status nginx
```

### 2. Перевірка health-ендпоінтів (напряму до застосунку)

```bash
curl http://127.0.0.1:5000/health/alive
# Очікується: 200 OK

curl http://127.0.0.1:5000/health/ready
# Очікується: 200 OK
```

### 3. Перевірка доступу через nginx

```bash
VM_IP="<IP адреса ВМ>"

# Кореневий ендпоінт
curl -H "Accept: text/html" http://$VM_IP/
# Очікується: HTML-сторінка зі списком ендпоінтів

# Health недоступний ззовні
curl http://$VM_IP/health/alive
# Очікується: 404
```

### 4. Перевірка бізнес-логіки

```bash
# Створити нотатку
curl -X POST http://$VM_IP/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "content": "Hello World"}'
# Очікується: {"status": "success", "message": "Note created"}, HTTP 201

# Отримати список нотаток (JSON)
curl -H "Accept: application/json" http://$VM_IP/notes
# Очікується: [{"id": 1, "title": "Test"}]

# Отримати список нотаток (HTML)
curl -H "Accept: text/html" http://$VM_IP/notes
# Очікується: HTML-таблиця з нотатками

# Отримати нотатку за ID
curl -H "Accept: application/json" http://$VM_IP/notes/1
# Очікується: {"id": 1, "title": "Test", "created_at": "...", "content": "Hello World"}

# Неіснуюча нотатка
curl -H "Accept: application/json" http://$VM_IP/notes/999
# Очікується: {"error": "Note not found"}, HTTP 404
```

### 5. Перевірка мережевої ізоляції БД

```bash
# БД не повинна бути доступна ззовні (виконати з іншої машини)
nc -zv <VM_IP> 3306
# Очікується: з'єднання відхилено

# Застосунок не повинен бути доступний напряму ззовні
nc -zv <VM_IP> 5000
# Очікується: з'єднання відхилено
```

### 6. Перевірка прав користувачів

```bash
# Увійти як operator і перевірити sudo-права
su - operator
sudo systemctl status mywebapp.service  # має працювати
sudo systemctl status nginx             # має НЕ працювати (не в списку)
sudo apt install curl                   # має НЕ працювати
```

### 7. Перевірка gradebook

```bash
cat /home/student/gradebook
# Очікується: 24
```
