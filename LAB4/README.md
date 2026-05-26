# Лабораторна робота №4 — IaC: Terraform + Ansible

| Компонент     | Адреса            | Порт |
| ------------- | ----------------- | ---- |
| nginx         | 0.0.0.0           | 80   |
| Notes Service | 127.0.0.1         | 5000 |
| MariaDB       | IP VM2 (VM1 only) | 3306 |

## Крок 1 — Підготовка SSH-ключів

```bash
# Ключ для ansible (автоматизація, без пароля)
ssh-keygen -t ed25519 -f ~/.ssh/ansible_id_rsa -N ""

# Ваш особистий ключ (якщо ще не існує)
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519
```

---

## Крок 2 — Розгортання інфраструктури (Terraform)

```bash
cd LAB4/terraform

# 1. Скопіюйте та заповніть конфіг змінних
cp terraform.tfvars.example terraform.tfvars
# Відкрийте terraform.tfvars та вставте свої SSH-ключі:
#   ansible_ssh_public_key = "$(cat ~/.ssh/ansible_id_rsa.pub)"
#   student_ssh_public_key = "$(cat ~/.ssh/id_ed25519.pub)"

# 2. Ініціалізуйте провайдер
terraform init

# 3. Перегляньте план (опційно)
terraform plan

# 4. Застосуйте — підніме обидві VM одною командою
terraform apply -auto-approve
```

Після виконання Terraform виведе IP-адреси VM:

```
worker_ip = "192.168.100.10"
db_ip     = "192.168.100.20"
```

---

## Крок 3 — Оновлення Ansible inventory

```bash
# Скопіюйте готовий inventory з outputs Terraform
terraform output -raw ansible_inventory > ../ansible/inventory.ini

# Або вручну відредагуйте ansible/inventory.ini:
# [workers]
# worker ansible_host=<worker_ip> ansible_user=ansible ansible_ssh_private_key_file=~/.ssh/ansible_id_rsa
# [db]
# db ansible_host=<db_ip> ansible_user=ansible ansible_ssh_private_key_file=~/.ssh/ansible_id_rsa
```

---

## Крок 4 — Налаштування конфігурації (Ansible)

```bash
cd LAB4/ansible

# Перевірте зв'язок з VM
ansible all -m ping

# Запустіть playbook — налаштує все одним запуском
ansible-playbook playbook.yml
```

Playbook виконає:

1. Встановлення базових пакетів на всіх VM
2. Створення користувачів teacher, operator, app
3. MariaDB на VM2 з обмеженим доступом
4. Notes Service на VM1 із systemd
5. nginx як reverse proxy на VM1
6. Firewall — порт 3306 доступний лише з VM1

### Повторний запуск (ідемпотентність)

```bash
# Безпечно запускати повторно — змін не буде якщо конфігурація актуальна
ansible-playbook playbook.yml
```

---

## Перевірка розгортання

### Health checks

```bash
WORKER_IP="192.168.100.10"

# /health/alive — застосунок живий
curl http://$WORKER_IP/health/alive
# Очікується: OK (200)

# /health/ready — застосунок підключений до БД
curl http://$WORKER_IP/health/ready
# Очікується: READY (200)
```

### API нотаток

```bash
# Створити нотатку
curl -X POST http://$WORKER_IP/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "content": "Hello from LAB4"}'

# Отримати список
curl -H "Accept: application/json" http://$WORKER_IP/notes

# Отримати нотатку за ID
curl -H "Accept: application/json" http://$WORKER_IP/notes/1
```

### Мережева ізоляція БД

```bash
DB_IP="192.168.100.20"

# БД недоступна ззовні
nc -zv $DB_IP 3306
# Очікується: Connection refused

# Застосунок недоступний напряму
nc -zv $WORKER_IP 5000
# Очікується: Connection refused
```

### Перевірка прав користувачів

```bash
# SSH як teacher
ssh teacher@$WORKER_IP  # пароль: 12345678

# SSH як operator
ssh operator@$WORKER_IP  # пароль: 12345678

# operator може тільки керувати сервісом та nginx
sudo systemctl restart mywebapp.service  # ✓ працює
sudo apt install curl                    # ✗ заборонено
```

### Gradebook

```bash
ssh ansible@$WORKER_IP "cat /home/student/gradebook"
# Очікується: 24
```

---

## Знищення інфраструктури

```bash
cd LAB4/terraform
terraform destroy -auto-approve
```
