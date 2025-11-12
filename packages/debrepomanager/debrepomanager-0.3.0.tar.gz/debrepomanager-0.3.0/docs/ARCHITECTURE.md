# Архитектура Debian Repository Manager

## Общая концепция

Система построена вокруг утилиты `aptly` с добавлением удобного CLI интерфейса и GitHub Actions интеграции.

## Ключевые архитектурные решения

### 1. Изоляция через Multi-Root Aptly

**Проблема**: aptly использует симлинки для оптимизации хранения и не поддерживает пакеты с одинаковым названием и версией, но разным содержимым в одном pool.

**Решение**: Используем отдельные aptly root директории для каждого codename (bookworm, noble, trixie и т.д.).

```
/srv/aptly/
├── bookworm/
│   ├── .aptly/
│   │   ├── db/
│   │   └── pool/
│   └── public/ -> /srv/repo/public/bookworm/
├── noble/
│   ├── .aptly/
│   │   ├── db/
│   │   └── pool/
│   └── public/ -> /srv/repo/public/noble/
└── trixie/
    ├── .aptly/
    │   ├── db/
    │   └── pool/
    └── public/ -> /srv/repo/public/trixie/
```

**Преимущества**:
- Полная изоляция pools между codenames
- Пакеты с одинаковым названием/версией но разным содержимым могут существовать в разных codenames
- Независимое управление каждым codename
- Проще backup и восстановление

**Недостатки**:
- Дублирование одинаковых пакетов между codenames (но это нормально для нашего случая)
- Немного больше места на диске

### 2. Атомарность через Snapshots

**Workflow добавления пакетов**:

```
1. Local Repo (мutable)
   ↓
2. Snapshot (immutable) с timestamp
   ↓
3. Published endpoint (атомарно переключается)
```

**Пример**:
```bash
# Добавляем пакеты в local repo
aptly repo add jethome-tools-bookworm package.deb

# Создаем snapshot
aptly snapshot create jethome-tools-bookworm-20251029-143022 from repo jethome-tools-bookworm

# Публикуем или переключаем (атомарно)
aptly publish switch bookworm jethome-tools jethome-tools-bookworm-20251029-143022
```

**Преимущества**:
- Мгновенное переключение (изменение симлинка)
- Возможность отката на предыдущий snapshot
- История изменений через список snapshots

### 3. Структура публикации

**URL схема**: `http://repo.site.com/{codename}/{component}`

**Пример apt конфигурации**:
```
deb http://repo.site.com/bookworm jethome-tools main
deb http://repo.site.com/bookworm jethome-armbian main
```

**Файловая структура на сервере**:
```
/srv/repo/public/
├── bookworm/
│   ├── jethome-tools/
│   │   ├── dists/
│   │   │   └── jethome-tools/
│   │   │       ├── main/
│   │   │       │   ├── binary-amd64/Packages
│   │   │       │   ├── binary-arm64/Packages
│   │   │       │   └── binary-riscv64/Packages
│   │   │       ├── Release
│   │   │       └── Release.gpg
│   │   └── pool/
│   │       └── main/
│   │           └── [пакеты]
│   ├── jethome-armbian/
│   │   ├── dists/
│   │   └── pool/
│   └── jethome-bookworm/
│       ├── dists/
│       └── pool/
├── noble/
│   └── ...
└── trixie/
    └── ...
```

**Aptly publish команда**:
```bash
# Структура: aptly publish [snapshot|repo] -distribution=<dist> -component=<comp> <name> <prefix>
aptly publish snapshot -distribution=jethome-tools jethome-tools-bookworm-20251029 bookworm/jethome-tools
```

### 4. Retention Policy

**Модель**:
```python
class RetentionPolicy:
    min_versions: int      # Минимальное количество версий для сохранения
    max_age_days: int      # Максимальный возраст в днях (старше удаляются)
```

**Логика применения**:
1. Группируем пакеты по названию
2. Сортируем версии (newest first)
3. Для каждого пакета:
   - Сохраняем последние `min_versions` версий (независимо от возраста)
   - Из оставшихся удаляем те, что старше `max_age_days`

**Пример**:
```yaml
retention:
  default:
    min_versions: 5
    max_age_days: 90
  overrides:
    jethome-armbian:
      min_versions: 3
      max_age_days: 60
```

Для пакета `mypackage` с 8 версиями:
- v1.0 (150 дней) - удалить (старше 90 дней и не входит в топ-5)
- v1.1 (120 дней) - удалить (старше 90 дней и не входит в топ-5)
- v1.2 (100 дней) - удалить (старше 90 дней и не входит в топ-5)
- v1.3 (80 дней) - сохранить (в топ-5)
- v1.4 (60 дней) - сохранить (в топ-5)
- v1.5 (40 дней) - сохранить (в топ-5)
- v1.6 (20 дней) - сохранить (в топ-5)
- v1.7 (5 дней) - сохранить (в топ-5)

### 5. GPG подпись

**Два режима работы**:

#### A. На сервере (интерактивный/полуавтоматический)
- GPG ключ импортирован в системный keyring
- `gpg-agent` настроен с кешированием passphrase
- TTL кеша: 8 часов (настраивается)
- При первом запуске CLI запрашивает passphrase
- Последующие операции используют кеш

**Настройка gpg-agent** (`~/.gnupg/gpg-agent.conf`):
```
default-cache-ttl 28800
max-cache-ttl 28800
```

#### B. В GitHub Actions (автоматический)
- GPG ключ в GitHub Secret (base64 encoded)
- Passphrase в отдельном secret
- Импорт ключа в начале workflow
- **Обязательная** очистка ключа в конце (always block)

**Workflow пример**:
```yaml
- name: Import GPG key
  run: |
    echo "${{ secrets.GPG_PRIVATE_KEY }}" | base64 -d | gpg --batch --import
    echo "${{ secrets.GPG_PASSPHRASE }}" | gpg --batch --passphrase-fd 0 --quick-add-key ...

- name: Add packages
  run: debrepomanager add ...

- name: Cleanup GPG
  if: always()
  run: gpg --batch --delete-secret-keys ${{ secrets.GPG_KEY_ID }}
```

### 6. Конфигурация

**Двухуровневая система**:

1. **config.yaml** в репозитории (defaults, шаблоны)
2. **/etc/repomanager/config.yaml** на сервере (overrides, secrets)

**Порядок мерджа**:
```python
config = load_config("./config.yaml")  # базовый
if exists("/etc/repomanager/config.yaml"):
    server_config = load_config("/etc/repomanager/config.yaml")
    config = merge(config, server_config)  # сервер имеет приоритет
```

**Приоритет значений**: CLI args > Server config > Repo config > Defaults

### 7. Компонентная структура

```
┌─────────────────────────────────────────────┐
│              CLI (cli.py)                    │
│  - argparse/click                            │
│  - команды: add, cleanup, create-repo и т.д. │
└─────────────┬───────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────┐
│         Config (config.py)                   │
│  - Загрузка YAML                             │
│  - Мерджинг                                  │
│  - Получение настроек                        │
└─────────────┬───────────────────────────────┘
              │
      ┌───────┴────────┬──────────────┐
      ↓                ↓              ↓
┌───────────┐   ┌──────────┐   ┌──────────┐
│  Aptly    │   │   GPG    │   │Retention │
│ (aptly.py)│   │ (gpg.py) │   │(retention│
│           │   │          │   │   .py)   │
└─────┬─────┘   └────┬─────┘   └────┬─────┘
      │              │              │
      └──────────────┴──────────────┘
                     │
              ┌──────┴────────┐
              ↓               ↓
        ┌──────────┐    ┌──────────┐
        │ aptly    │    │   gpg    │
        │ (binary) │    │ (binary) │
        └──────────┘    └──────────┘
```

## Workflow сценарии

### Сценарий 1: Добавление пакетов из CI/CD

```
GitHub Actions (build пакетов)
    ↓
Upload artifacts
    ↓
GitHub Actions (add-packages workflow)
    ↓ (rsync)
Сервер: /tmp/packages/
    ↓
debrepomanager add --package-dir /tmp/packages/ --codename bookworm --component jethome-tools
    ↓
aptly repo add → snapshot → publish switch
    ↓
http://repo.site.com/bookworm/jethome-tools (обновлен атомарно)
```

### Сценарий 2: Cleanup старых пакетов

```
GitHub Actions (schedule: weekly)
    ↓ (SSH)
repomanager cleanup --dry-run (preview)
    ↓
repomanager cleanup --apply
    ↓
Для каждого компонента:
  - Получить список пакетов
  - Применить retention policy
  - Удалить из aptly repo
  - Создать новый snapshot
  - Publish switch
    ↓
Отчет в GitHub Actions summary
```

### Сценарий 3: Создание нового репозитория

```
debrepomanager create-repo --codename trixie --component jethome-tools
    ↓
1. Создать aptly root для trixie (если не существует)
2. Создать aptly local repo: jethome-tools-trixie
3. Создать пустой snapshot
4. Опубликовать: aptly publish snapshot ... trixie/jethome-tools
    ↓
http://repo.site.com/trixie/jethome-tools (готов к использованию)
```

## Безопасность

### SSH доступ из GitHub Actions
- Использование `webfactory/ssh-agent` action
- SSH ключ только с правами на запись в `/tmp/` и выполнение `repomanager`
- Ограничение в `~/.ssh/authorized_keys`:
  ```
  command="/usr/local/bin/repomanager-wrapper",no-port-forwarding,no-X11-forwarding ssh-rsa AAAA...
  ```

### GPG ключи
- В GitHub Secrets храним base64 encoded private key
- Passphrase в отдельном secret
- Обязательная очистка после использования
- На сервере: защищенный keyring, gpg-agent с TTL

### Права доступа
```
/srv/aptly/          - root:repomanager, 775
/srv/repo/public/    - www-data:repomanager, 775
/etc/repomanager/    - root:root, 750 (config.yaml: 640)
```

## Масштабирование

### Текущая архитектура
- Один сервер
- Синхронные операции
- Блокировка на уровне aptly

### Возможности расширения
1. **Несколько серверов**: rsync published директорий на mirror серверы
2. **Load balancing**: DNS round-robin или nginx upstream
3. **CDN**: CloudFlare/CloudFront перед repo.site.com
4. **Distributed**: aptly API server + несколько воркеров

## Ограничения и компромиссы

### Дублирование пакетов
Одинаковые пакеты дублируются между codenames (из-за изоляции pools).
**Альтернатива**: shared pool, но тогда проблема с разным содержимым.
**Решение**: дублирование приемлемо, disk space дешевле чем проблемы с симлинками.

### Блокировка при операциях
Aptly не поддерживает параллельные операции на одном репозитории.
**Решение**: очередь задач или простая блокировка (lockfile).

### Откат изменений
Snapshots позволяют откат, но нужно вручную найти правильный snapshot.
**Решение**: хранить мета-информацию о snapshots (timestamp, changelog).

## Мониторинг и отладка

### Логирование
- CLI: вывод в stdout/stderr + файл `/var/log/repomanager/repomanager.log`
- Уровни: DEBUG, INFO, WARNING, ERROR
- Формат: timestamp, level, component, message

### Метрики (опционально, будущее)
- Количество пакетов по repo
- Размер pools
- Количество snapshots
- Время выполнения операций

### Health checks
- `debrepomanager verify`: проверка консистентности
- Проверка GPG подписей
- Проверка свободного места на диске

