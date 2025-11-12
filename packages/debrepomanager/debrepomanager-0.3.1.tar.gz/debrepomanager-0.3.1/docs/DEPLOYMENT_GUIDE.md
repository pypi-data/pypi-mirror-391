# Инструкция по развертыванию Debian Repository Manager

**Сценарий**: Новая система с пакетами в `armbian/{system}/`  
**Цель**: Создать репозитории для bookworm, noble, jammy с коллекцией jethome-{system}  
**URL для клиентов**: `http://repo.site.com/beta`

---

## 1. Подготовка системы

### Установка зависимостей

```bash
# Обновление системы
sudo apt update
sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    gnupg \
    apt-utils \
    nginx

# Установка aptly
wget -qO - https://www.aptly.info/pubkey.txt | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/aptly.gpg
echo "deb http://repo.aptly.info/ squeeze main" | sudo tee /etc/apt/sources.list.d/aptly.list
sudo apt update
sudo apt install -y aptly
```

---

## 2. Создание GPG ключа для подписи

```bash
# Генерация GPG ключа
gpg --full-generate-key

# Выберите:
# - RSA and RSA
# - 4096 bits
# - Does not expire (или установите срок)
# - Real name: JetHome Repository
# - Email: repo@jethome.ru
# - Passphrase: (установите надежный пароль или оставьте пустым)

# Получить Key ID
gpg --list-secret-keys --keyid-format=long

# Вывод будет примерно:
# sec   rsa4096/1234567890ABCDEF 2025-11-03
#       ^^^^^^^^^^^^^^^^^^^^
# Скопируйте Key ID (1234567890ABCDEF)

# Экспорт публичного ключа для клиентов
sudo mkdir -p /opt/repo
sudo gpg --armor --export 1234567890ABCDEF | sudo tee /opt/repo/pubkey.gpg

# Настройка gpg-agent для кеширования пароля (опционально)
mkdir -p ~/.gnupg
cat >> ~/.gnupg/gpg-agent.conf <<EOF
default-cache-ttl 28800
max-cache-ttl 28800
allow-preset-passphrase
EOF
gpg-connect-agent reloadagent /bye
```

---

## 3. Установка repomanager

```bash
# Клонирование репозитория
cd /opt
sudo git clone https://github.com/jethome-iot/repomanager.git
cd repomanager

# Установка зависимостей
sudo pip3 install --break-system-packages -e .
# ИЛИ создать venv (рекомендуется):
sudo python3 -m venv /opt/repomanager-venv
sudo /opt/repomanager-venv/bin/pip install -e .

# Создать symlink для удобства
sudo ln -s /opt/repomanager-venv/bin/repomanager /usr/local/bin/repomanager

# Проверка установки
repomanager --help
```

---

## 4. Настройка конфигурации

```bash
# Создать директорию для конфигурации
sudo mkdir -p /etc/repomanager

# Создать конфигурационный файл
sudo tee /etc/debrepomanager/config.yaml > /dev/null <<EOF
aptly:
  # Базовая директория для aptly (изолированные roots для каждого codename)
  root_base: /opt/repo/aptly
  
  # Публичная директория для HTTP доступа
  # /opt/repo/beta/{codename}/{component}/
  publish_base: /opt/repo/beta

gpg:
  # Ваш GPG Key ID (замените на реальный!)
  key_id: "1234567890ABCDEF"
  use_agent: true

repositories:
  # Поддерживаемые системы
  codenames:
    - bookworm
    - noble
    - jammy
    - trixie
  
  # Компоненты (автоматические для каждой системы)
  components:
    - jethome-bookworm
    - jethome-noble
    - jethome-jammy
    - jethome-trixie
  
  # Архитектуры
  architectures:
    - amd64
    - arm64
    - riscv64
  
  # Автоматическое создание репозиториев
  auto_create: true
  
  # Поддержка старого и нового форматов URL
  dual_format:
    enabled: true
    method: symlink
    auto_symlink: true

retention:
  default:
    min_versions: 5
    max_age_days: 90

advanced:
  max_snapshots: 10
EOF

# Замените Key ID на реальный
sudo sed -i 's/1234567890ABCDEF/ВАШ_РЕАЛЬНЫЙ_KEY_ID/' /etc/debrepomanager/config.yaml
```

---

## 5. Создание структуры директорий

```bash
# Создание базовых директорий
sudo mkdir -p /opt/repo/aptly
sudo mkdir -p /opt/repo/beta

# Создание директорий для входящих пакетов (опционально)
sudo mkdir -p /opt/repo/incoming

# Установка прав
sudo chown -R $USER:$USER /opt/repo
chmod -R 755 /opt/repo
```

---

## 6. Создание репозиториев для всех систем

```bash
# Список систем в вашем случае
SYSTEMS="bookworm noble jammy"

# Создание репозиториев для каждой системы
for system in $SYSTEMS; do
    echo "=== Создание репозитория для $system ==="
    
    debrepomanager create-repo \
        --codename $system \
        --component jethome-$system
    
    echo "✓ Репозиторий $system/jethome-$system создан"
    echo ""
done

# Проверка созданных репозиториев
debrepomanager list
```

**Ожидаемый вывод:**
```
All repositories:
Total: 3

  jethome-bookworm-bookworm
  jethome-noble-noble
  jethome-jammy-jammy
```

---

## 7. Добавление пакетов из armbian/{system}/

### Вариант A: Автоматически для всех систем

```bash
# Скрипт для добавления пакетов из armbian/{system}/
cat > /tmp/add_all_packages.sh <<'SCRIPT'
#!/bin/bash

SYSTEMS="bookworm noble jammy"
ARMBIAN_BASE="/path/to/armbian"  # ЗАМЕНИТЕ на реальный путь!

for system in $SYSTEMS; do
    PKG_DIR="$ARMBIAN_BASE/$system"
    
    if [ ! -d "$PKG_DIR" ]; then
        echo "⚠️  Пропускаем $system - директория не найдена: $PKG_DIR"
        continue
    fi
    
    DEB_COUNT=$(find "$PKG_DIR" -name "*.deb" | wc -l)
    
    if [ "$DEB_COUNT" -eq 0 ]; then
        echo "⚠️  Нет пакетов в $PKG_DIR"
        continue
    fi
    
    echo "=== Добавление пакетов для $system ($DEB_COUNT packages) ==="
    
    debrepomanager add \
        --codename $system \
        --component jethome-$system \
        --package-dir "$PKG_DIR"
    
    echo "✓ Добавлено $DEB_COUNT пакетов в $system/jethome-$system"
    echo ""
done

echo "✅ Все пакеты добавлены!"
SCRIPT

chmod +x /tmp/add_all_packages.sh

# ВАЖНО: Замените путь в скрипте на реальный!
sed -i 's|/path/to/armbian|/реальный/путь/к/armbian|' /tmp/add_all_packages.sh

# Запуск
/tmp/add_all_packages.sh
```

### Вариант B: Вручную для каждой системы

```bash
# Bookworm
debrepomanager add \
    --codename bookworm \
    --component jethome-bookworm \
    --package-dir armbian/bookworm/

# Noble
debrepomanager add \
    --codename noble \
    --component jethome-noble \
    --package-dir armbian/noble/

# Jammy
debrepomanager add \
    --codename jammy \
    --component jethome-jammy \
    --package-dir armbian/jammy/
```

---

## 8. Проверка созданных репозиториев

```bash
# Список всех репозиториев
debrepomanager list

# Пакеты в конкретном репозитории
debrepomanager list --codename bookworm --component jethome-bookworm

# Проверка структуры на диске
ls -la /opt/repo/beta/bookworm/jethome-bookworm/
ls -la /opt/repo/beta/dists/bookworm/jethome-bookworm  # Symlink для старого формата

# Проверка Release файла
cat /opt/repo/beta/bookworm/jethome-bookworm/dists/jethome-bookworm/Release

# Проверка GPG подписи
gpg --verify \
    /opt/repo/beta/bookworm/jethome-bookworm/dists/jethome-bookworm/InRelease
```

---

## 9. Настройка nginx

```bash
# Создание конфигурации nginx
sudo tee /etc/nginx/sites-available/repo.site.com <<'EOF'
server {
    listen 80;
    server_name repo.site.com repo.site.com;
    
    # Корневая директория - /opt/repo
    root /opt/repo;
    
    # Логирование
    access_log /var/log/nginx/repo_access.log;
    error_log /var/log/nginx/repo_error.log;
    
    # Основная локация
    location / {
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;
    }
    
    # Кеширование метаданных репозитория
    location ~ /(InRelease|Release|Packages|Sources)(\.gz|\.bz2|\.xz)?$ {
        expires 1h;
        add_header Cache-Control "public, must-revalidate";
    }
    
    # Кеширование пакетов
    location ~ \.deb$ {
        expires 7d;
        add_header Cache-Control "public";
    }
}
EOF

# Активация конфигурации
sudo ln -s /etc/nginx/sites-available/repo.site.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 10. Проверка доступности репозитория

```bash
# Проверка HTTP доступа
curl -I http://repo.site.com/beta/bookworm/jethome-bookworm/dists/jethome-bookworm/Release
# Должен вернуть: HTTP/1.1 200 OK

# Проверка публичного ключа
curl http://repo.site.com/pubkey.gpg
# Должен вывести GPG ключ

# Проверка Packages файла
curl http://repo.site.com/beta/bookworm/jethome-bookworm/dists/jethome-bookworm/main/binary-amd64/Packages | head -20
```

---

## 11. Настройка клиентских систем

### На Debian Bookworm:

```bash
# Импорт GPG ключа
wget -qO - http://repo.site.com/pubkey.gpg | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/jethome.gpg

# Добавление репозитория
echo "deb http://repo.site.com/beta bookworm jethome-bookworm" | \
    sudo tee /etc/apt/sources.list.d/jethome.list

# Обновление
sudo apt update

# Проверка доступности пакетов
apt-cache policy | grep jethome

# Установка пакета (если есть)
sudo apt install имя-пакета
```

### На Ubuntu Noble:

```bash
# Импорт GPG ключа
wget -qO - http://repo.site.com/pubkey.gpg | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/jethome.gpg

# Добавление репозитория
echo "deb http://repo.site.com/beta noble jethome-noble" | \
    sudo tee /etc/apt/sources.list.d/jethome.list

# Обновление
sudo apt update
```

### На Ubuntu Jammy:

```bash
# Импорт GPG ключа
wget -qO - http://repo.site.com/pubkey.gpg | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/jethome.gpg

# Добавление репозитория
echo "deb http://repo.site.com/beta jammy jethome-jammy" | \
    sudo tee /etc/apt/sources.list.d/jethome.list

# Обновление
sudo apt update
```

---

## 12. Обновление конфигурации для /beta prefix

**ВАЖНО**: Ваш URL `http://repo.site.com/beta` требует специальной настройки!

### Обновите config.yaml:

```bash
sudo nano /etc/debrepomanager/config.yaml
```

Измените `publish_base`:

```yaml
aptly:
  root_base: /opt/repo/aptly
  # ВАЖНО: publish_base должен указывать на /opt/repo/beta
  publish_base: /opt/repo/beta
```

Структура будет:
```
/opt/repo/
├── beta/                         # publish_base
│   ├── bookworm/                 # codename
│   │   └── jethome-bookworm/     # component
│   │       ├── dists/
│   │       │   └── jethome-bookworm/
│   │       │       ├── Release
│   │       │       ├── InRelease
│   │       │       └── main/
│   │       │           ├── binary-amd64/
│   │       │           ├── binary-arm64/
│   │       │           └── binary-riscv64/
│   │       └── pool/
│   │           └── main/
│   │               └── j/
│   │                   └── jethome-*/
│   │                       └── *.deb
│   ├── noble/
│   │   └── jethome-noble/
│   └── jammy/
│       └── jethome-jammy/
├── aptly/                        # aptly databases
│   ├── bookworm/
│   ├── noble/
│   └── jammy/
└── pubkey.gpg                    # Публичный GPG ключ
```

**URL для клиентов:**
```
deb http://repo.site.com/beta bookworm jethome-bookworm
```

Это соответствует структуре:
```
/opt/repo/beta/bookworm/jethome-bookworm/dists/jethome-bookworm/
```

---

## 13. Полный скрипт развертывания

```bash
#!/bin/bash

set -e  # Exit on error

echo "=== Debian Repository Manager - Полная установка ==="
echo ""

# Переменные (ИЗМЕНИТЕ ПОД ВАШИ НУЖДЫ!)
REPO_BASE="/opt/repo"
PUBLISH_BASE="$REPO_BASE/beta"
ARMBIAN_BASE="/path/to/armbian"  # ЗАМЕНИТЕ!
SYSTEMS="bookworm noble jammy"
GPG_KEY_ID="1234567890ABCDEF"  # ЗАМЕНИТЕ!

echo "Настройки:"
echo "  Repo base: $REPO_BASE"
echo "  Publish base: $PUBLISH_BASE"
echo "  Armbian packages: $ARMBIAN_BASE"
echo "  Systems: $SYSTEMS"
echo "  GPG Key ID: $GPG_KEY_ID"
echo ""
read -p "Продолжить? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# 1. Создание директорий
echo "=== Шаг 1: Создание директорий ==="
sudo mkdir -p "$REPO_BASE/aptly"
sudo mkdir -p "$PUBLISH_BASE"
sudo chown -R $USER:$USER "$REPO_BASE"
echo "✓ Директории созданы"
echo ""

# 2. Создание конфигурации
echo "=== Шаг 2: Создание конфигурации ==="
sudo mkdir -p /etc/repomanager

sudo tee /etc/debrepomanager/config.yaml > /dev/null <<EOF
aptly:
  root_base: $REPO_BASE/aptly
  publish_base: $PUBLISH_BASE

gpg:
  key_id: "$GPG_KEY_ID"
  use_agent: true

repositories:
  codenames: [bookworm, noble, jammy, trixie]
  components: [jethome-bookworm, jethome-noble, jethome-jammy, jethome-trixie]
  architectures: [amd64, arm64, riscv64]
  auto_create: true
  dual_format:
    enabled: true
    method: symlink
    auto_symlink: true

retention:
  default:
    min_versions: 5
    max_age_days: 90

advanced:
  max_snapshots: 10
EOF

echo "✓ Конфигурация создана: /etc/debrepomanager/config.yaml"
echo ""

# 3. Экспорт публичного ключа
echo "=== Шаг 3: Экспорт GPG ключа ==="
gpg --armor --export "$GPG_KEY_ID" > "$REPO_BASE/pubkey.gpg"
echo "✓ Публичный ключ экспортирован: $REPO_BASE/pubkey.gpg"
echo ""

# 4. Создание репозиториев
echo "=== Шаг 4: Создание репозиториев ==="
for system in $SYSTEMS; do
    echo "Создание репозитория: $system/jethome-$system"
    
    debrepomanager create-repo \
        --codename $system \
        --component jethome-$system
    
    echo "✓ $system/jethome-$system создан"
done
echo ""

# 5. Добавление пакетов
echo "=== Шаг 5: Добавление пакетов ==="
for system in $SYSTEMS; do
    PKG_DIR="$ARMBIAN_BASE/$system"
    
    if [ ! -d "$PKG_DIR" ]; then
        echo "⚠️  Пропускаем $system - директория не найдена: $PKG_DIR"
        continue
    fi
    
    DEB_COUNT=$(find "$PKG_DIR" -name "*.deb" | wc -l)
    
    if [ "$DEB_COUNT" -eq 0 ]; then
        echo "⚠️  Нет .deb пакетов в $PKG_DIR"
        continue
    fi
    
    echo "Добавление $DEB_COUNT пакетов в $system/jethome-$system"
    
    debrepomanager add \
        --codename $system \
        --component jethome-$system \
        --package-dir "$PKG_DIR"
    
    echo "✓ $DEB_COUNT пакетов добавлено в $system/jethome-$system"
    echo ""
done

# 6. Финальная проверка
echo "=== Шаг 6: Проверка ==="
debrepomanager list
echo ""

echo "=== Структура репозитория ==="
tree -L 4 "$PUBLISH_BASE" 2>/dev/null || find "$PUBLISH_BASE" -maxdepth 4 -type d
echo ""

echo "✅ Развертывание завершено!"
echo ""
echo "Следующие шаги:"
echo "1. Настройте nginx (см. секцию 9)"
echo "2. Проверьте HTTP доступ: curl -I http://repo.site.com/beta/bookworm/jethome-bookworm/dists/jethome-bookworm/Release"
echo "3. Настройте клиентов (см. секцию 11)"
EOF

# Сделать скрипт исполняемым
chmod +x /tmp/deploy_repo.sh

# ПЕРЕД ЗАПУСКОМ: отредактируйте переменные!
nano /tmp/deploy_repo.sh

# Запуск
/tmp/deploy_repo.sh
```

---

## 14. Пошаговые команды (минимальный вариант)

### Если у вас уже есть пакеты в `/srv/armbian/{system}/`:

```bash
# 1. Установка repomanager (см. шаг 3)

# 2. Создание config.yaml
sudo tee /etc/debrepomanager/config.yaml > /dev/null <<EOF
aptly:
  root_base: /opt/repo/aptly
  publish_base: /opt/repo/beta
gpg:
  key_id: "ВАШ_GPG_KEY_ID"  # Замените!
  use_agent: true
repositories:
  codenames: [bookworm, noble, jammy]
  components: [jethome-bookworm, jethome-noble, jethome-jammy]
  architectures: [amd64, arm64, riscv64]
  auto_create: true
  dual_format:
    enabled: true
    method: symlink
    auto_symlink: true
EOF

# 3. Создание и наполнение репозиториев
for system in bookworm noble jammy; do
    debrepomanager add \
        --codename $system \
        --component jethome-$system \
        --package-dir /srv/armbian/$system/
done

# 4. Проверка
debrepomanager list

# 5. Экспорт GPG ключа
gpg --armor --export ВАШ_GPG_KEY_ID > /opt/repo/pubkey.gpg

# 6. Настройка nginx (см. шаг 9)

# Готово!
```

---

## 15. Настройка клиентов - автоматический скрипт

Создайте скрипт для клиентов:

```bash
cat > /tmp/setup_jethome_repo.sh <<'SCRIPT'
#!/bin/bash

# Определение системы
if [ -f /etc/os-release ]; then
    . /etc/os-release
    CODENAME=$VERSION_CODENAME
else
    CODENAME=$(lsb_release -cs)
fi

echo "Система: $ID $CODENAME"

# Поддерживаемые системы
if [[ ! "$CODENAME" =~ ^(bookworm|noble|jammy|trixie)$ ]]; then
    echo "⚠️  Неподдерживаемая система: $CODENAME"
    echo "Поддерживаются: bookworm, noble, jammy, trixie"
    exit 1
fi

# Импорт GPG ключа
echo "Импорт GPG ключа..."
wget -qO - http://repo.site.com/pubkey.gpg | \
    sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/jethome.gpg

# Добавление репозитория
echo "Добавление репозитория JetHome..."
echo "deb http://repo.site.com/beta $CODENAME jethome-$CODENAME" | \
    sudo tee /etc/apt/sources.list.d/jethome.list

# Обновление
echo "Обновление списков пакетов..."
sudo apt update

echo "✅ Репозиторий JetHome настроен для $CODENAME!"
echo ""
echo "Пакеты доступны для установки через: sudo apt install <package>"
SCRIPT

chmod +x /tmp/setup_jethome_repo.sh
```

Распространите этот скрипт клиентам:
```bash
# На клиенте:
curl -O http://repo.site.com/setup_jethome_repo.sh
chmod +x setup_jethome_repo.sh
./setup_jethome_repo.sh
```

---

## 16. Обслуживание и обновление

### Добавление новых пакетов

```bash
# Добавление пакетов в существующий репозиторий
debrepomanager add \
    --codename bookworm \
    --component jethome-bookworm \
    --packages /path/to/new-package.deb

# Или из директории
debrepomanager add \
    --codename bookworm \
    --component jethome-bookworm \
    --package-dir /srv/armbian/bookworm/
```

### Создание нового репозитория для новой системы

```bash
# Например, для trixie
debrepomanager create-repo \
    --codename trixie \
    --component jethome-trixie

# Добавление пакетов
debrepomanager add \
    --codename trixie \
    --component jethome-trixie \
    --package-dir /srv/armbian/trixie/
```

### Просмотр содержимого

```bash
# Список репозиториев
debrepomanager list

# Пакеты в репозитории
debrepomanager list --codename bookworm --component jethome-bookworm
```

---

## 17. Troubleshooting

### Проблема: GPG signing fails

```bash
# Проверить наличие ключа
gpg --list-secret-keys

# Проверить gpg-agent
gpg-connect-agent 'keyinfo --list' /bye

# Перезапустить gpg-agent
gpgconf --kill gpg-agent
gpg-connect-agent /bye

# Тестовая подпись
echo "test" | gpg --clearsign
```

### Проблема: aptly errors

```bash
# Проверить конфигурацию
cat /etc/debrepomanager/config.yaml

# Проверить aptly напрямую
aptly -config /opt/repo/aptly/bookworm/aptly.conf repo list

# Проверить публикации
aptly -config /opt/repo/aptly/bookworm/aptly.conf publish list
```

### Проблема: nginx 404

```bash
# Проверить путь к файлам
ls -la /opt/repo/beta/bookworm/jethome-bookworm/dists/jethome-bookworm/Release

# Проверить конфигурацию nginx
sudo nginx -t

# Проверить логи
sudo tail -f /var/log/nginx/repo_error.log
```

### Проблема: apt update fails на клиенте

```bash
# Проверить GPG ключ
apt-key list | grep -A 2 jethome

# Проверить sources.list
cat /etc/apt/sources.list.d/jethome.list

# Проверить доступность через curl
curl -I http://repo.site.com/beta/bookworm/jethome-bookworm/dists/jethome-bookworm/Release

# Подробный вывод
sudo apt update -o Debug::Acquire::http=true
```

---

## 18. Автоматизация через cron

### Ежедневное добавление новых пакетов

```bash
# Создать скрипт
sudo tee /opt/repo/update_repos.sh > /dev/null <<'SCRIPT'
#!/bin/bash

SYSTEMS="bookworm noble jammy"
ARMBIAN_BASE="/srv/armbian"

for system in $SYSTEMS; do
    if [ -d "$ARMBIAN_BASE/$system" ]; then
        /usr/local/bin/debrepomanager add \
            --codename $system \
            --component jethome-$system \
            --package-dir "$ARMBIAN_BASE/$system/" \
            2>&1 | logger -t repomanager
    fi
done
SCRIPT

sudo chmod +x /opt/repo/update_repos.sh

# Добавить в cron (ежедневно в 2:00)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/repo/update_repos.sh") | crontab -
```

---

## 19. Быстрая справка - команды

### Создание репозитория
```bash
debrepomanager create-repo --codename <system> --component jethome-<system>
```

### Добавление пакетов
```bash
debrepomanager add --codename <system> --component jethome-<system> --package-dir /path/to/packages/
```

### Просмотр
```bash
debrepomanager list                                    # Все репозитории
debrepomanager list --codename <system>                # Репозитории системы
debrepomanager list --codename <system> --component <component>  # Пакеты
```

### Удаление (осторожно!)
```bash
debrepomanager delete-repo --codename <system> --component <component> --confirm
```

---

## 20. Проверочный чеклист

После развертывания проверьте:

- [ ] repomanager установлен: `debrepomanager --version`
- [ ] GPG ключ создан: `gpg --list-secret-keys`
- [ ] Конфигурация создана: `cat /etc/debrepomanager/config.yaml`
- [ ] Репозитории созданы: `debdebrepomanager list`
- [ ] Пакеты добавлены: `debdebrepomanager list --codename bookworm --component jethome-bookworm`
- [ ] Структура на диске: `ls -la /opt/repo/beta/bookworm/jethome-bookworm/`
- [ ] Symlinks созданы: `ls -la /opt/repo/beta/dists/bookworm/`
- [ ] nginx настроен: `nginx -t`
- [ ] HTTP доступ работает: `curl -I http://repo.site.com/beta/bookworm/jethome-bookworm/dists/jethome-bookworm/Release`
- [ ] Публичный ключ доступен: `curl http://repo.site.com/pubkey.gpg`
- [ ] apt update работает на клиенте

---

## 📝 Примечания

### Структура URL

**Ваш формат:** `deb http://repo.site.com/beta bookworm jethome-bookworm`

Разбор:
- `http://repo.site.com/beta` - базовый URL (nginx root: /opt/repo, запрос к /beta)
- `bookworm` - codename (система клиента)
- `jethome-bookworm` - component (коллекция пакетов)

Соответствует файлам:
```
/opt/repo/beta/bookworm/jethome-bookworm/dists/jethome-bookworm/Release
/opt/repo/beta/bookworm/jethome-bookworm/dists/jethome-bookworm/main/binary-amd64/Packages
```

### Dual Format

Старый формат также будет работать (через symlinks):
```
deb http://repo.site.com/beta/dists bookworm jethome-bookworm
```

Но рекомендуется использовать новый формат (первый вариант).

---

## 📞 Помощь

- **Documentation**: https://github.com/jethome-iot/repomanager
- **Issues**: https://github.com/jethome-iot/repomanager/issues
- **Quick Start**: docs/QUICKSTART.md
- **Configuration**: docs/CONFIG.md

**Готово! Ваш репозиторий развернут! 🚀**

