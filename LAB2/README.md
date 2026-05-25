# Лабораторна робота №2 — Контейнеризація

## Мета

Дослідити підходи контейнеризації застосунків та автоматизувати запуск сервісів з Лабораторної роботи №1 за допомогою Docker Compose.

---

## Структура репозиторію

```
TRPZ-labs/
├── LAB1/
│   ├── app/
│   │   ├── app.py
│   │   ├── migrate.py
│   │   ├── entrypoint.sh
│   │   ├── requirements.txt
│   │   └── dockerfile        
│   ├── nginx/
│   │   └── nginx.conf
│   ├── docker-compose.yml
│   └── README.md
└── LAB2/
    └── README.md             ← цей файл
```

---

## Практична частина — Docker Compose

### Архітектура

```
client
  │
  ▼
nginx (0.0.0.0:80)        ← єдина точка входу
  │
  ▼
web / Flask (:5000)       ← застосунок у контейнері
  │
  ▼
db / MariaDB (:3306)      ← база даних у контейнері
```

Усі сервіси працюють в ізольованій мережі `notes_network`. Назовні відкритий лише порт `80`. Дані БД зберігаються у named volume `db_data` і переживають будь-який перезапуск.

### Передумови

- [Docker](https://docs.docker.com/get-docker/) 20.10+
- Docker Compose plugin (`docker compose version`)

### Запуск

```bash
# Клонувати репозиторій
git clone https://github.com/XzenoeR/TRPZ-labs.git
cd TRPZ-labs/LAB1

# Зібрати образи та запустити у фоні
docker compose up --build -d
```

### Перевірка стану

```bash
docker compose ps
docker compose logs -f
```

Очікуваний вивід `docker compose ps`:

```
NAME             IMAGE           STATUS    PORTS
lab1-db-1        mariadb:latest  Up
lab1-web-1       lab1-web        Up
lab1-nginx-1     nginx:latest    Up        0.0.0.0:80->80/tcp
```

### Тестування

```bash
# Створити нотатку
curl -X POST http://localhost/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "content": "Hello from Docker"}'

# Отримати список нотаток
curl -H "Accept: application/json" http://localhost/notes

# Отримати нотатку за ID
curl -H "Accept: application/json" http://localhost/notes/1
```

### Зупинка

```bash
# Зупинити контейнери (дані БД збережуться)
docker compose down

# Зупинити та видалити дані БД
docker compose down -v
```

