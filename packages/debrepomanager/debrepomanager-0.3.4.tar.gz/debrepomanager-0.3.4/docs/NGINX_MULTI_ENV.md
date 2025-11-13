# Nginx Configuration for Multi-Environment Setup

Настройка Nginx для поддержки stable/beta/test репозиториев.

## Обзор

Конфигурация поддерживает три окружения:
- **Stable**: `http://deb.repo.com/` (production)
- **Beta**: `http://deb.repo.com/beta/` (pre-release testing)
- **Test**: `http://deb.repo.com/test/` (development testing)

## Структура директорий

```
/srv/repo/
├── public/          # Stable repository
│   ├── bookworm/
│   ├── noble/
│   └── ...
├── public-beta/     # Beta repository
│   ├── bookworm/
│   ├── noble/
│   └── ...
└── public-test/     # Test repository
    ├── bookworm/
    ├── noble/
    └── ...

/srv/aptly/
├── stable/          # Stable aptly root
│   ├── bookworm/
│   ├── noble/
│   └── ...
├── beta/            # Beta aptly root
│   ├── bookworm/
│   ├── noble/
│   └── ...
└── test/            # Test aptly root
    ├── bookworm/
    ├── noble/
    └── ...
```

## Nginx конфигурация

### /etc/nginx/sites-available/deb-repo

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name deb.repo.com;

    # Общие настройки
    access_log /var/log/nginx/deb-repo-access.log;
    error_log /var/log/nginx/deb-repo-error.log;

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/x-debian-package;
    gzip_min_length 1024;

    # === STABLE Repository (root path) ===
    location / {
        root /srv/repo/public;
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;

        # Allow large package downloads
        client_max_body_size 500M;

        # Cache headers for packages
        location ~* \.(deb|udeb)$ {
            expires 7d;
            add_header Cache-Control "public, immutable";
        }

        # Cache headers for metadata
        location ~* (Packages|Release|InRelease)$ {
            expires 1h;
            add_header Cache-Control "public, must-revalidate";
        }
    }

    # === BETA Repository ===
    location /beta/ {
        alias /srv/repo/public-beta/;
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;

        # Allow large package downloads
        client_max_body_size 500M;

        # Cache headers for packages
        location ~* \.(deb|udeb)$ {
            expires 3d;
            add_header Cache-Control "public";
        }

        # Cache headers for metadata
        location ~* (Packages|Release|InRelease)$ {
            expires 30m;
            add_header Cache-Control "public, must-revalidate";
        }
    }

    # === TEST Repository ===
    location /test/ {
        alias /srv/repo/public-test/;
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;

        # Allow large package downloads
        client_max_body_size 500M;

        # No caching for test
        location ~* \.(deb|udeb|Packages|Release|InRelease)$ {
            expires -1;
            add_header Cache-Control "no-store, no-cache, must-revalidate";
        }
    }

    # GPG public key
    location /pubkey.gpg {
        alias /srv/repo/pubkey.gpg;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
}

# HTTPS redirect (if SSL configured)
server {
    listen 80;
    listen [::]:80;
    server_name deb.repo.com;

    # Let's Encrypt ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name deb.repo.com;

    # SSL certificates (configure with your certificates)
    ssl_certificate /etc/letsencrypt/live/deb.repo.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/deb.repo.com/privkey.pem;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Same location blocks as HTTP server
    # (copy from above)
}
```

## Установка и активация

### 1. Создать директории

```bash
sudo mkdir -p /srv/repo/public
sudo mkdir -p /srv/repo/public-beta
sudo mkdir -p /srv/repo/public-test

sudo mkdir -p /srv/aptly/stable
sudo mkdir -p /srv/aptly/beta
sudo mkdir -p /srv/aptly/test

# Права доступа
sudo chown -R repomanager:repomanager /srv/aptly/
sudo chown -R repomanager:www-data /srv/repo/
sudo chmod -R 775 /srv/repo/
```

### 2. Установить конфигурацию Nginx

```bash
# Создать конфиг
sudo nano /etc/nginx/sites-available/deb-repo

# Проверить синтаксис
sudo nginx -t

# Активировать
sudo ln -s /etc/nginx/sites-available/deb-repo /etc/nginx/sites-enabled/

# Перезапустить
sudo systemctl reload nginx
```

### 3. Экспортировать GPG ключ

```bash
# Экспортировать публичный ключ
gpg --armor --export YOUR_KEY_ID > /srv/repo/pubkey.gpg
sudo chown www-data:www-data /srv/repo/pubkey.gpg
```

### 4. Настроить конфигурации debrepomanager

```bash
# Stable
sudo cp config-stable.yaml.example /etc/repomanager/config-stable.yaml
sudo nano /etc/repomanager/config-stable.yaml  # Настроить GPG key_id

# Beta
sudo cp config-beta.yaml.example /etc/repomanager/config-beta.yaml
sudo nano /etc/repomanager/config-beta.yaml

# Test
sudo cp config-test.yaml.example /etc/repomanager/config-test.yaml
sudo nano /etc/repomanager/config-test.yaml
```

## Использование

### Загрузка пакетов

**В stable:**
```bash
REPOMANAGER_CONFIG=/etc/repomanager/config-stable.yaml \
    scripts/repoadd stable bookworm armbian-bookworm
```

**В beta:**
```bash
REPOMANAGER_CONFIG=/etc/repomanager/config-beta.yaml \
    scripts/repoadd beta noble jethome-tools
```

**В test:**
```bash
REPOMANAGER_CONFIG=/etc/repomanager/config-test.yaml \
    scripts/repoadd test bookworm ./packages/
```

### Настройка клиентов

**Stable repository:**
```bash
# Import GPG key
wget -qO - http://deb.repo.com/pubkey.gpg | \
    sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/jethome.gpg

# Add repository
echo "deb http://deb.repo.com/ bookworm jethome-armbian-bookworm" | \
    sudo tee /etc/apt/sources.list.d/jethome.list

# Update
sudo apt update
```

**Beta repository:**
```bash
# Import GPG key
wget -qO - http://deb.repo.com/pubkey.gpg | \
    sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/jethome.gpg

# Add repository
echo "deb http://deb.repo.com/beta/ noble jethome-tools" | \
    sudo tee /etc/apt/sources.list.d/jethome-beta.list

# Update
sudo apt update
```

**Test repository:**
```bash
# Import GPG key
wget -qO - http://deb.repo.com/pubkey.gpg | \
    sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/jethome.gpg

# Add repository
echo "deb http://deb.repo.com/test/ bookworm jethome-packages" | \
    sudo tee /etc/apt/sources.list.d/jethome-test.list

# Update
sudo apt update
```

## Monitoring

### Проверка работоспособности

```bash
# Health check
curl http://deb.repo.com/health

# Проверка stable
curl -I http://deb.repo.com/bookworm/jethome-tools/

# Проверка beta
curl -I http://deb.repo.com/beta/bookworm/jethome-tools/

# Проверка test
curl -I http://deb.repo.com/test/bookworm/jethome-tools/
```

### Логи

```bash
# Access logs
sudo tail -f /var/log/nginx/deb-repo-access.log

# Error logs
sudo tail -f /var/log/nginx/deb-repo-error.log

# Filter by environment
sudo grep "/beta/" /var/log/nginx/deb-repo-access.log
sudo grep "/test/" /var/log/nginx/deb-repo-access.log
```

### Статистика

```bash
# Количество запросов по окружениям
sudo awk '{print $7}' /var/log/nginx/deb-repo-access.log | \
    grep -E "^/(beta|test)/" | sort | uniq -c

# Топ загружаемых пакетов
sudo awk '{print $7}' /var/log/nginx/deb-repo-access.log | \
    grep "\.deb$" | sort | uniq -c | sort -rn | head -20
```

## Безопасность

### Ограничение доступа к test

Если нужно ограничить доступ к test репозиторию:

```nginx
location /test/ {
    # Basic auth
    auth_basic "Test Repository";
    auth_basic_user_file /etc/nginx/.htpasswd-test;

    alias /srv/repo/public-test/;
    autoindex on;
}
```

Создать пароль:
```bash
sudo htpasswd -c /etc/nginx/.htpasswd-test testuser
```

### IP whitelist для test

```nginx
location /test/ {
    # Allow only specific IPs
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;

    alias /srv/repo/public-test/;
    autoindex on;
}
```

## Troubleshooting

### 403 Forbidden

```bash
# Проверить права
ls -la /srv/repo/public/
ls -la /srv/repo/public-beta/
ls -la /srv/repo/public-test/

# Исправить
sudo chown -R repomanager:www-data /srv/repo/
sudo chmod -R 755 /srv/repo/
```

### 404 Not Found

```bash
# Проверить существование директорий
ls -la /srv/repo/public/bookworm/
ls -la /srv/repo/public-beta/bookworm/
ls -la /srv/repo/public-test/bookworm/

# Проверить symlinks
ls -la /srv/repo/public/dists/
```

### Медленная загрузка

```bash
# Проверить gzip
curl -H "Accept-Encoding: gzip" -I http://deb.repo.com/bookworm/jethome-tools/

# Включить кеширование в nginx (см. конфиг выше)
```

## См. также

- [REPOADD_SCRIPT.md](REPOADD_SCRIPT.md) - Документация repoadd
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Общее руководство по развертыванию
- [APT_CONFIGURATION.md](APT_CONFIGURATION.md) - Настройка клиентов

