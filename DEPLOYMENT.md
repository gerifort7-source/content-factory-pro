# Content Factory Pro - Инструкции по развертыванию

## 🚀 Production Development Guide

Этот документ содержит инструкции по развертыванию Content Factory Pro на различные облачные платформы.

## 📋 Требования перед развертыванием

### Необходимые сервисы и ключи:
- ✅ OpenAI API Key (для генерации контента)
- ✅ Telegram Bot Token (для интеграции)
- ✅ PostgreSQL Database (production)
- ✅ Redis Instance (для кеширования)
- ✅ SECRET_KEY для JWT аутентификации

### Переменные окружения:

```bash
# Приложение
APP_NAME=content-factory-pro
DEBUG=false
DOMIN=yourdomain.com

# JWT
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://user:password@host:5432/content_factory
DATABASE_ECHO=false

# Redis
REDIS_URL=redis://user:password@host:6379/0

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_ADMIN_CHAT_ID=your_chat_id

# Logging
LOG_LEVEL=INFO
```

## 🐳 Option 1: Deploy на Render

### Step 1: Подготовка кода

```bash
# Push код на GitHub
git add .
git commit -m "Ready for production"
git push origin main
```

### Step 2: Создание PostgreSQL базы на Render

1. Перейди на render.com
2. Click "New" → "PostgreSQL"
3. Выбери регион (Europe/US)
4. Сохрани database URL

### Step 3: Создание Web Service

1. Click "New" → "Web Service"
2. Подключи GitHub репозиторий
3. Выбери branch `main`
4. Runtime: `Python 3.10`
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 4: Установка переменных окружения

В Render Dashboard → Environment:

```
DATABASE_URL = postgresql://...
REDIS_URL = redis://...
OPENAI_API_KEY = sk-...
TELEGRAM_BOT_TOKEN = ...
SECRET_KEY = your-secure-key
```

### Step 5: Deploy

Render автоматически развернет приложение.

---

## 🚄 Option 2: Deploy на Railway

### Step 1: Установка Railway CLI

```bash
npm install -g @railway/cli
railway login
```

### Step 2: Инициализация проекта

```bash
railway init
```

### Step 3: Добавление сервисов

```bash
# PostgreSQL
railway add --plugin postgres

# Redis
railway add --plugin redis
```

### Step 4: Конфигурация

Создай `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

### Step 5: Развертывание

```bash
railway up
```

---

## 🌐 Option 3: Deploy на Heroku (legacy)

### Step 1: Установка Heroku CLI

```bash
curl https://cli-assets.heroku.com/install.sh | sh
heroku login
```

### Step 2: Создание приложения

```bash
heroku create content-factory-pro
```

### Step 3: Добавление PostgreSQL

```bash
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:premium-0
```

### Step 4: Установка переменных

```bash
heroku config:set SECRET_KEY=your-key
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set TELEGRAM_BOT_TOKEN=...
```

### Step 5: Deploy

```bash
git push heroku main
```

---

## 🐧 Option 4: Deploy на VPS (Ubuntu 22.04)

### Step 1: SSH подключение

```bash
ssh root@your_server_ip
```

### Step 2: Обновление системы

```bash
apt update && apt upgrade -y
apt install -y python3-pip python3-venv postgresql redis-server nginx
```

### Step 3: Клонирование проекта

```bash
cd /opt
git clone https://github.com/yourusername/content-factory-pro.git
cd content-factory-pro
```

### Step 4: Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 5: Конфигурация Systemd

Создай `/etc/systemd/system/content-factory.service`:

```ini
[Unit]
Description=Content Factory Pro
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/content-factory-pro
ExecStart=/opt/content-factory-pro/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 6: Запуск сервиса

```bash
systemctl daemon-reload
systemctl enable content-factory
systemctl start content-factory
```

### Step 7: Конфигурация Nginx

Создай `/etc/nginx/sites-available/content-factory`:

```nginx
upstream content_factory {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://content_factory;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Step 8: SSL с Let's Encrypt

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com
```

---

## ✅ Post-Deployment Setup

### 1. Инициализация базы данных

```bash
# Миграция таблиц
python -c "from database.session import init_db; init_db()"
```

### 2. Проверка здоровья приложения

```bash
curl https://yourdomain.com/health
```

### 3. Доступ к API документации

```
https://yourdomain.com/docs (Swagger UI)
https://yourdomain.com/redoc (ReDoc)
```

### 4. Мониторинг логов

```bash
# На Render/Railway
railway logs

# На VPS
journalctl -u content-factory -f
```

---

## 🔧 Трубешутинг

### Проблема: 502 Bad Gateway

```bash
# Проверь статус приложения
railway logs
# или
journalctl -u content-factory -xe
```

### Проблема: Database connection error

```bash
# Проверь DATABASE_URL
echo $DATABASE_URL

# Тест подключения
psql $DATABASE_URL -c "SELECT 1"
```

### Проблема: Telegram не работает

```bash
# Проверь token
curl https://api.telegram.org/botYOUR_TOKEN/getMe

# Проверь webhook
curl https://yourdomain.com/telegram/webhook
```

---

## 📊 Monitoring & Logs

### Настройка логирования

Уже настроено в `core/config.py`:

```python
LOG_LEVEL = "INFO"
```

### Рекомендуемые сервисы мониторинга:
- 🔍 **Sentry** - Error tracking
- 📊 **DataDog** - Performance monitoring
- 📝 **Papertrail** - Log aggregation

---

## 🔐 Безопасность

### Чеклист безопасности перед production:

- [ ] Изменен `SECRET_KEY`
- [ ] `DEBUG = False`
- [ ] Все API ключи в переменных окружения
- [ ] CORS настроен правильно
- [ ] SSL сертификат установлен
- [ ] Регулярные резервные копии БД
- [ ] Логирование ошибок включено
- [ ] Rate limiting настроен

---

## 📈 Масштабирование

После запуска можно масштабировать:

1. **Горизонтальное**: Увеличить количество инстансов
2. **Вертикальное**: Увеличить CPU/RAM
3. **Кеширование**: Оптимизировать Redis
4. **CDN**: Добавить CloudFlare

---

## 💬 Поддержка

Если возникли проблемы:

1. Проверь логи
2. Изучи документацию платформы
3. Откройте Issue на GitHub

🎉 Успешного развертывания!
