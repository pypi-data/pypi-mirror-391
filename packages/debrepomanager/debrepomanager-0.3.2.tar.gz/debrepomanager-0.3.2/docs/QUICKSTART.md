# Quick Start Guide

Быстрый старт для Debian Repository Manager.

## 🚀 За 5 минут

### Установка на сервере

```bash
# 1. Установить aptly
wget -qO - https://www.aptly.info/pubkey.txt | gpg --dearmor > /etc/apt/trusted.gpg.d/aptly.gpg
echo "deb http://repo.aptly.info/ squeeze main" > /etc/apt/sources.list.d/aptly.list
apt update && apt install aptly

# 2. Клонировать и установить repomanager
git clone https://github.com/jethome/repomanager.git /opt/repomanager
cd /opt/repomanager
pip3 install -e .

# 3. Создать конфигурацию
cp config.yaml.example /etc/debrepomanager/config.yaml
vim /etc/debrepomanager/config.yaml
# Установить: gpg.key_id, aptly.root_base, aptly.publish_base

# 4. Импортировать GPG ключ (если нужно)
gpg --import /path/to/your-key.asc

# 5. Настроить gpg-agent
cat >> ~/.gnupg/gpg-agent.conf <<EOF
default-cache-ttl 28800
max-cache-ttl 28800
EOF
gpg-connect-agent reloadagent /bye
```

### Первый репозиторий

#### Способ 1: Упрощенный (repoadd script)

```bash
# Загрузить пакеты одной командой (автосоздание репо, если не существует)
scripts/repoadd stable bookworm armbian-bookworm

# Для beta окружения
scripts/repoadd beta noble jethome-tools

# Для test окружения
scripts/repoadd test bookworm ./packages/
```

См. [REPOADD_SCRIPT.md](REPOADD_SCRIPT.md) для подробностей.

#### Способ 2: Ручной (debrepomanager CLI)

```bash
# Создать репозиторий
debrepomanager create-repo --codename bookworm --component jethome-tools

# Добавить пакеты
debrepomanager add --codename bookworm --component jethome-tools \
    --package-dir /path/to/packages/

# Проверить
debrepomanager list --codename bookworm --component jethome-tools
```

### Настройка веб-сервера (nginx)

```nginx
server {
    listen 80;
    server_name repo.site.com;

    root /srv/repo/public;

    location / {
        autoindex on;
    }

    # Кеширование метаданных репозитория
    location ~ /(Release|Packages|Sources)(\.gz|\.bz2|\.xz)?$ {
        expires 1h;
    }
}
```

## 📦 Использование в системе

### Добавить репозиторий на клиенте

```bash
# 1. Импортировать GPG ключ
wget -qO - http://repo.site.com/pubkey.gpg | \
    gpg --dearmor > /etc/apt/trusted.gpg.d/jethome.gpg

# 2. Добавить источник
cat > /etc/apt/sources.list.d/jethome.list <<EOF
deb http://repo.site.com/bookworm jethome-tools main
deb http://repo.site.com/bookworm jethome-armbian main
EOF

# 3. Обновить и установить
apt update
apt install <package-name>
```

**📖 Для других систем (Noble, Trixie, Jammy)**: см. полные примеры в [APT_CONFIGURATION.md](APT_CONFIGURATION.md)

## 🤖 GitHub Actions Setup

### 1. Настроить Secrets

В GitHub repository Settings → Secrets and variables → Actions:

- `SSH_PRIVATE_KEY`: SSH ключ для доступа к серверу
- `SSH_HOST`: repo.site.com
- `SSH_USER`: repomanager
- `GPG_PRIVATE_KEY`: `cat key.asc | base64 -w0`
- `GPG_PASSPHRASE`: пароль от ключа
- `GPG_KEY_ID`: ID ключа

### 2. Создать workflow для добавления пакетов

`.github/workflows/publish-packages.yml`:

```yaml
name: Build and Publish Packages

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build packages
        run: ./build-packages.sh
      - name: Upload packages
        uses: actions/upload-artifact@v3
        with:
          name: packages
          path: output/*.deb

  publish:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          repository: jethome/repomanager
          path: repomanager

      - name: Download packages
        uses: actions/download-artifact@v3
        with:
          name: packages
          path: ./packages

      - name: Setup SSH
        uses: webfactory/ssh-agent@v0.8.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - name: Transfer packages
        run: |
          TEMP_DIR="/tmp/packages-${{ github.run_id }}"
          rsync -avz ./packages/ \
            ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }}:$TEMP_DIR/

      - name: Add to repository
        run: |
          ssh ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }} \
            "debrepomanager add \
              --codename bookworm \
              --component jethome-tools \
              --package-dir $TEMP_DIR && \
             rm -rf $TEMP_DIR"
```

## 🧹 Автоматическая очистка

### Retention Policy

Автоматическая очистка старых версий пакетов на основе политик:

**Настройка в `/etc/debrepomanager/config.yaml`:**

```yaml
retention:
  default:
    min_versions: 5      # Минимум версий (всегда сохраняются)
    max_age_days: 90     # Удалять старше 90 дней (если больше min_versions)

  overrides:
    jethome-testing:     # Для тестовых пакетов
      min_versions: 2
      max_age_days: 14
```

**Логика**: Всегда сохраняются последние 5 версий. Если версий больше, то удаляются те что старше 90 дней.

### Команда cleanup

**Dry-run (показать что будет удалено):**
```bash
debrepomanager cleanup --codename bookworm --component jethome-tools
```

**Реальное удаление:**
```bash
debrepomanager cleanup --codename bookworm --component jethome-tools --apply
```

**С verbose выводом:**
```bash
debrepomanager cleanup --codename bookworm --component jethome-tools -v
```

### Настроить периодическую очистку

`.github/workflows/cleanup.yml`:

```yaml
name: Cleanup Old Packages

on:
  schedule:
    - cron: '0 2 * * 0'  # Еженедельно в воскресенье 2:00
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: webfactory/ssh-agent@v0.8.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - name: Cleanup repositories
        run: |
          ssh ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }} \
            "debrepomanager cleanup --codename bookworm --component jethome-tools --apply"
```

## 📋 Основные команды

```bash
# Создать репозиторий
debrepomanager create-repo --codename <codename> --component <component>

# Добавить пакеты
debrepomanager add --codename <codename> --component <component> \
    --packages file1.deb file2.deb
# или из директории
debrepomanager add --codename <codename> --component <component> \
    --package-dir /path/to/dir/

# Список репозиториев
debrepomanager list
debrepomanager list --codename bookworm
debrepomanager list --codename bookworm --component jethome-tools

# Очистка старых версий (dry-run)
debrepomanager cleanup --codename bookworm --component jethome-tools

# Очистка (реальное удаление)
debrepomanager cleanup --codename bookworm --component jethome-tools --apply

# Удалить репозиторий
debrepomanager delete-repo --codename <codename> --component <component> --confirm

# Проверка консистентности
repomanager verify --codename <codename> --component <component>
```

## ⚙️ Retention Policy

Настройка в `/etc/debrepomanager/config.yaml`:

```yaml
retention:
  default:
    min_versions: 5      # Минимум версий (всегда сохраняются)
    max_age_days: 90     # Удалять старше 90 дней (если больше min_versions)

  overrides:
    jethome-testing:     # Для тестовых пакетов
      min_versions: 2
      max_age_days: 14
```

**Логика**: Всегда сохраняются последние 5 версий. Если версий больше, то удаляются те что старше 90 дней.

## 🔍 Troubleshooting

### GPG signing не работает

```bash
# Проверить ключ
gpg --list-secret-keys

# Перезапустить gpg-agent
gpgconf --kill gpg-agent
gpg-connect-agent /bye

# Установить GPG_TTY
export GPG_TTY=$(tty)
```

### Aptly ошибки

```bash
# Проверить репозитории
aptly repo list

# Проверить published
aptly publish list

# Очистить orphaned files
aptly db cleanup
```

### Права доступа

```bash
# Исправить права на aptly root
chown -R repomanager:repomanager /srv/aptly/
chmod -R 775 /srv/aptly/

# Исправить права на publish directory
chown -R www-data:repomanager /srv/repo/public/
chmod -R 775 /srv/repo/public/
```

## 📚 Дальнейшее чтение

- [README.md](README.md) - Полная документация
- [CONFIG.md](CONFIG.md) - Детальное описание конфигурации
- [ARCHITECTURE.md](ARCHITECTURE.md) - Архитектура системы
- [DEVELOPMENT.md](DEVELOPMENT.md) - Для разработчиков

## 💬 Поддержка

- Issues: https://github.com/jethome/repomanager/issues
- Email: support@jethome.ru

