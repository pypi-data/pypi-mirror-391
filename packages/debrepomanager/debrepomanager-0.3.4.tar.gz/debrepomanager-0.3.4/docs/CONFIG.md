# Configuration Reference

Полное описание всех параметров конфигурации Debian Repository Manager (v0.2+).

## Configuration Priority Chain

**debrepomanager** использует стандартную цепочку поиска конфигурации (как git, docker, npm):

### Priority Order (от низкого к высокому):

1. **System-wide**: `/etc/debrepomanager/config.yaml` (самый низкий приоритет)
2. **User-level**: `~/.debrepomanager/config.yaml`
3. **Local directory**: `./config.yaml` (cwd)
4. **Explicit --config**: Если указан `--config path`, используется только он
5. **Environment variables**: `REPOMANAGER_*` (высший приоритет)

### Как работает

```bash
# Auto-detection (loads all found configs in priority order)
debrepomanager list

# Explicit config (ignores other locations)
debrepomanager --config /path/to/config.yaml list

# Environment override (highest priority)
export REPOMANAGER_APTLY_ROOT_BASE=/custom/path
debrepomanager list  # Uses /custom/path
```

### Расположение файлов

- **System**: `/etc/debrepomanager/config.yaml` - настройки сервера
- **User**: `~/.debrepomanager/config.yaml` - пользовательские настройки
- **Local**: `./config.yaml` - настройки для текущей директории
- **Example**: `config.yaml.example` - шаблон с описанием всех опций

## Environment Variables

Переменные окружения имеют наивысший приоритет и переопределяют любые файлы:

| Environment Variable | Config Path | Example |
|---------------------|-------------|---------|
| `REPOMANAGER_APTLY_ROOT_BASE` | `aptly.root_base` | `/srv/aptly` |
| `REPOMANAGER_APTLY_PUBLISH_BASE` | `aptly.publish_base` | `/srv/repo/public` |
| `REPOMANAGER_GPG_KEY_ID` | `gpg.key_id` | `ABC123DEF456` |
| `REPOMANAGER_GPG_USE_AGENT` | `gpg.use_agent` | `true` |

**Example**:
```bash
# Override GPG key for specific operation
REPOMANAGER_GPG_KEY_ID=TESTKEY123 debrepomanager create-repo bookworm test-repo
```

## Структура конфигурации

### GPG

Настройки GPG подписи репозиториев.

```yaml
gpg:
  key_id: "1234567890ABCDEF"
  use_agent: true
  gpg_path: "/usr/bin/gpg"
```

#### `gpg.key_id` (обязательный)
- **Тип**: string
- **Описание**: ID GPG ключа для подписи репозиториев
- **Пример**: `"1234567890ABCDEF"` или `"user@example.com"`
- **Как получить**: `gpg --list-keys` (последние 16 символов)

#### `gpg.use_agent` (опциональный)
- **Тип**: boolean
- **По умолчанию**: `true`
- **Описание**: Использовать gpg-agent для кеширования passphrase
- **Рекомендация**: `true` для серверного использования, `false` для CI/CD

#### `gpg.gpg_path` (опциональный)
- **Тип**: string
- **По умолчанию**: автоопределение через `which gpg`
- **Описание**: Путь к исполняемому файлу gpg
- **Пример**: `"/usr/bin/gpg2"`

---

### Aptly

Настройки путей и конфигурации aptly.

```yaml
aptly:
  root_base: "/srv/aptly"
  publish_base: "/srv/repo/public"
  aptly_path: "/usr/bin/aptly"
```

#### `aptly.root_base` (обязательный)
- **Тип**: string
- **Описание**: Базовая директория для aptly roots
- **Структура**: Для каждого codename создается поддиректория:
  ```
  /srv/aptly/
    ├── bookworm/
    ├── noble/
    └── trixie/
  ```
- **Права доступа**: должна быть доступна для записи пользователю repomanager
- **Пример**: `"/srv/aptly"`, `"/var/lib/aptly"`

#### `aptly.publish_base` (обязательный)
- **Тип**: string
- **Описание**: Базовая директория для published репозиториев (веб-сервер root)
- **Структура**:
  ```
  /srv/repo/public/
    ├── bookworm/
    │   ├── jethome-tools/
    │   └── jethome-armbian/
    └── noble/
        └── jethome-tools/
  ```
- **Права доступа**: должна быть доступна для чтения веб-серверу (www-data)
- **Пример**: `"/srv/repo/public"`, `"/var/www/repo"`

#### `aptly.aptly_path` (опциональный)
- **Тип**: string
- **По умолчанию**: автоопределение через `which aptly`
- **Описание**: Путь к исполняемому файлу aptly
- **Пример**: `"/usr/local/bin/aptly"`

---

### Retention

Политики хранения старых версий пакетов.

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

#### `retention.default` (обязательный)
Политика по умолчанию для всех компонентов.

##### `retention.default.min_versions`
- **Тип**: integer
- **По умолчанию**: `5`
- **Описание**: Минимальное количество версий пакета для сохранения (независимо от возраста)
- **Логика**: Всегда сохраняются последние N версий, даже если они старше `max_age_days`
- **Рекомендация**: 3-10 в зависимости от частоты релизов

##### `retention.default.max_age_days`
- **Тип**: integer
- **По умолчанию**: `90`
- **Описание**: Максимальный возраст пакета в днях
- **Логика**: Пакеты старше этого срока удаляются, если их больше чем `min_versions`
- **Рекомендация**: 30-180 дней
##### `retention.default.keep_latest` (NEW in v0.2+)
- **Тип**: integer
- **По умолчанию**: `1`
- **Описание**: Сколько самых свежих версий сохранять независимо от возраста
- **Назначение**: Защита недавних версий от удаления даже если они превысили `max_age_days`
- **Логика**: Итоговое количество версий = `max(min_versions, keep_latest)`
- **Примеры**:
  - `keep_latest: 1` - всегда сохранять новейшую версию (default, безопасно)
  - `keep_latest: 2` - всегда сохранять 2 новейшие версии даже если старые
  - `keep_latest: 0` - отключить защиту (использовать только min_versions)
- **Use case**: Если релизы редкие, но нужно сохранять последнюю версию

##### `retention.default.delete_last_aged_version` (NEW in v0.2+)
- **Тип**: boolean
- **По умолчанию**: `false`  
- **Описание**: Разрешить удаление последней оставшейся версии пакета если она превысила max_age_days
- **Безопасность**:
  - `false` (default) - всегда сохранять хотя бы одну версию пакета (безопасно!)
  - `true` - может полностью удалить пакет если все версии слишком старые (опасно!)
- **Рекомендация**: Оставить `false` для production packages
- **Use case**: `true` для temporary/debug packages которые можно полностью удалить
- **⚠️ Предупреждение**: `delete_last_aged_version: true` может полностью удалить пакет!
- **Примеры**:
  ```yaml
  # Production (default): never delete last version
  delete_last_aged_version: false
  
  # Debug packages: can delete completely
  delete_last_aged_version: true  # Осторожно!
  ```


#### `retention.overrides` (опциональный)
Специфичные политики для отдельных компонентов.

- **Тип**: dict[component_name -> policy]
- **Описание**: Переопределения политики для конкретных компонентов
- **Пример**:
  ```yaml
  overrides:
    jethome-armbian:  # Меньше версий для зеркала armbian
      min_versions: 3
      max_age_days: 60
    jethome-debug:    # Более агрессивная очистка для debug пакетов
      min_versions: 2
      max_age_days: 30
    jethome-lts:      # Дольше храним LTS пакеты
      min_versions: 10
      max_age_days: 365
  ```

#### Использование Retention Policy

**Команда cleanup:**

```bash
# Dry-run (показать что будет удалено, без реального удаления)
debrepomanager cleanup --codename bookworm --component jethome-tools

# Реальное удаление пакетов
debrepomanager cleanup --codename bookworm --component jethome-tools --apply

# С verbose выводом
debrepomanager cleanup --codename bookworm --component jethome-tools -v --apply
```

**Логика работы:**

1. Получить все версии каждого пакета
2. Отсортировать по версии (debian version comparison)
3. **Всегда** оставить последние `min_versions` версий
4. Из оставшихся версий удалить те, что старше `max_age_days`

**Пример:**

Если в репозитории 10 версий пакета `my-app`:
- Версии: 1.0, 1.1, 1.2, ..., 1.9, 2.0
- Настройки: `min_versions: 5`, `max_age_days: 90`
- Возраст пакетов: 1.0-1.5 старше 90 дней, остальные свежее

**Результат:**
- Сохраняются: 2.0, 1.9, 1.8, 1.7, 1.6 (5 новейших)
- Кандидаты на удаление: 1.5, 1.4, 1.3, 1.2, 1.1, 1.0
- Удаляются: 1.0-1.5 (все старше 90 дней)

---

### Repositories

Конфигурация репозиториев.

```yaml
repositories:
  codenames:
    - bookworm
    - noble
    - trixie
    - jammy
  components:
    - jethome-tools
    - jethome-armbian
    - jethome-bookworm
  architectures:
    - amd64
    - arm64
    - riscv64
  auto_create: true
```

#### `repositories.codenames` (REMOVED in v0.2+)
- **Status**: Deprecated - удалено в v0.2.0
- **Why**: Codenames создаются динамически при создании репозиториев
- **Migration**: Просто удалите эту секцию из config.yaml
- **Usage**: Используйте любой codename при создании репозитория:
  ```bash
  debrepomanager create-repo bookworm jethome-tools
  debrepomanager create-repo noble my-custom-repo
  debrepomanager create-repo trixie any-component-name
  ```

#### `repositories.components` (REMOVED in v0.2+)
- **Status**: Deprecated - удалено в v0.2.0
- **Why**: Components создаются динамически при создании репозиториев
- **Migration**: Просто удалите эту секцию из config.yaml
- **Usage**: Используйте любой component при создании репозитория:
  ```bash
  debrepomanager add --codename bookworm --component my-tools *.deb
  ```

#### Repository Metadata (NEW in v0.2+)
- **Location**: `{aptly_root_base}/.repomanager/metadata.json`
- **Purpose**: Tracks all created repositories for fast listing
- **Format**:
  ```json
  {
    "repositories": [
      {"codename": "bookworm", "component": "tools", "created": "2025-11-05T10:00:00Z"},
      {"codename": "noble", "component": "armbian", "created": "2025-11-05T11:00:00Z"}
    ],
    "last_updated": "2025-11-05T12:00:00Z"
  }
  ```
- **Sync**: Run `debrepomanager sync` to rebuild from actual aptly state
- **Auto-updated**: On `create-repo` and `delete-repo` operations

#### `repositories.architectures` (обязательный)
- **Тип**: list[string]
- **Описание**: Список поддерживаемых архитектур
- **Стандартные значения**: amd64, arm64, armhf, i386, riscv64, ppc64el
- **Пример**:
  ```yaml
  architectures:
    - amd64    # x86_64
    - arm64    # ARMv8
    - riscv64  # RISC-V 64-bit
  ```

#### `repositories.auto_create` (опциональный)
- **Тип**: boolean
- **По умолчанию**: `true`
- **Описание**: Автоматически создавать репозиторий при добавлении пакетов
- **Логика**:
  - `true`: Если репозиторий не существует, создается автоматически
  - `false`: При попытке добавить пакеты в несуществующий репозиторий - ошибка
- **Рекомендация**: `true` для CI/CD, `false` для production с ручным управлением

---

### Logging

Настройки логирования.

```yaml
logging:
  level: "INFO"
  file: "/var/log/repomanager/repomanager.log"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

#### `logging.level` (опциональный)
- **Тип**: string
- **По умолчанию**: `"INFO"`
- **Допустимые значения**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Описание**: Уровень детализации логов
- **Рекомендация**:
  - `DEBUG`: для разработки и отладки
  - `INFO`: для production
  - `WARNING`: для минимального логирования

#### `logging.file` (опциональный)
- **Тип**: string
- **По умолчанию**: `null` (логи только в stdout)
- **Описание**: Путь к файлу логов
- **Пример**: `"/var/log/repomanager/repomanager.log"`
- **Права доступа**: директория должна существовать и быть доступна для записи

#### `logging.format` (опциональный)
- **Тип**: string
- **По умолчанию**: `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"`
- **Описание**: Формат строки лога (Python logging format)
- **Пример**: `"[%(levelname)s] %(message)s"` (упрощенный)

---

### Advanced

Расширенные настройки.

```yaml
advanced:
  max_snapshots: 10
  snapshot_format: "{component}-{codename}-%Y%m%d-%H%M%S"
  parallel: false
  cleanup_dry_run_default: true
```

#### `advanced.max_snapshots` (опциональный)
- **Тип**: integer
- **По умолчанию**: `10`
- **Описание**: Максимальное количество snapshots на компонент
- **Логика**: При превышении лимита старые snapshots удаляются автоматически
- **Рекомендация**: 5-20 (баланс между историей и местом на диске)

#### `advanced.snapshot_format` (опциональный)
- **Тип**: string (strftime format)
- **По умолчанию**: `"{component}-{codename}-%Y%m%d-%H%M%S"`
- **Описание**: Формат имени snapshot'а
- **Плейсхолдеры**:
  - `{component}`: название компонента
  - `{codename}`: codename дистрибутива
  - strftime форматы: `%Y`, `%m`, `%d`, `%H`, `%M`, `%S`
- **Пример**: `"jethome-tools-bookworm-20251029-143022"`

#### `advanced.parallel` (опциональный)
- **Тип**: boolean
- **По умолчанию**: `false`
- **Описание**: Включить параллельную обработку репозиториев
- **Статус**: Зарезервировано для будущего, пока не реализовано

#### `advanced.cleanup_dry_run_default` (опциональный)
- **Тип**: boolean
- **По умолчанию**: `true`
- **Описание**: Dry-run режим по умолчанию для cleanup операций
- **Безопасность**: `true` предотвращает случайное удаление пакетов

---

## Примеры конфигураций

### Минимальная конфигурация

```yaml
gpg:
  key_id: "YOUR_KEY_ID"

aptly:
  root_base: "/srv/aptly"
  publish_base: "/srv/repo/public"

repositories:
  codenames: [bookworm]
  components: [main]
  architectures: [amd64]
```

### Production конфигурация

```yaml
gpg:
  key_id: "1234567890ABCDEF"
  use_agent: true

aptly:
  root_base: "/srv/aptly"
  publish_base: "/srv/repo/public"

retention:
  default:
    min_versions: 5
    max_age_days: 90
  overrides:
    jethome-lts:
      min_versions: 10
      max_age_days: 365
    jethome-testing:
      min_versions: 2
      max_age_days: 14

repositories:
  codenames:
    - bookworm
    - trixie
    - noble
    - jammy
  components:
    - jethome-tools
    - jethome-armbian
    - jethome-lts
    - jethome-testing
  architectures:
    - amd64
    - arm64
    - riscv64
  auto_create: false

logging:
  level: "INFO"
  file: "/var/log/repomanager/repomanager.log"

advanced:
  max_snapshots: 15
  cleanup_dry_run_default: true
```

### Development конфигурация

```yaml
gpg:
  key_id: "DEV_KEY_ID"
  use_agent: true

aptly:
  root_base: "/tmp/test-aptly"
  publish_base: "/tmp/test-repo"

retention:
  default:
    min_versions: 2
    max_age_days: 7

repositories:
  codenames: [bookworm]
  components: [test]
  architectures: [amd64]
  auto_create: true

logging:
  level: "DEBUG"
```

---

## Переменные окружения

Некоторые параметры можно переопределить через переменные окружения:

- `REPOMANAGER_CONFIG`: путь к конфигурационному файлу
- `REPOMANAGER_LOG_LEVEL`: уровень логирования
- `GPG_TTY`: для корректной работы gpg-agent (должна быть установлена в `$(tty)`)

**Пример**:
```bash
export REPOMANAGER_CONFIG=/custom/path/config.yaml
export REPOMANAGER_LOG_LEVEL=DEBUG
export GPG_TTY=$(tty)

debrepomanager list
```

---

## Валидация конфигурации

Проверить корректность конфигурации:

```bash
repomanager --config config.yaml validate
```

Возможные ошибки:
- Отсутствие обязательных параметров
- Некорректные пути (не существуют или нет прав доступа)
- Недоступность GPG ключа
- Неустановленный aptly

---

## Repository Metadata Management

### Metadata File

**Location**: `{aptly_root_base}/.repomanager/metadata.json`

Metadata file automatically tracks all created repositories for fast listing without scanning all aptly roots.

**Structure**:
```json
{
  "repositories": [
    {
      "codename": "bookworm",
      "component": "jethome-tools",
      "created": "2025-11-05T10:00:00.000000"
    }
  ],
  "last_updated": "2025-11-05T12:30:00.000000"
}
```

### Automatic Updates

Metadata is automatically updated on:
- `create-repo` - adds repository
- `delete-repo` - removes repository
- `sync` - rebuilds from actual aptly state

### Sync Command (NEW in v0.2)

Rebuild metadata from actual aptly repository state:

```bash
# Sync metadata with actual state
debrepomanager sync

# With verbose output
debrepomanager --verbose sync
```

**When to use**:
- After manual aptly operations
- After migrating from v0.1.x
- To recover from metadata corruption
- After restoring from backup

**What it does**:
1. Scans all codename directories under `aptly_root_base`
2. Finds all aptly repositories  
3. Rebuilds metadata.json from scratch
4. Returns count of repositories found

---

## Migration from v0.1.x to v0.2.0

### Required Steps

1. **Update package**:
   ```bash
   pip install --upgrade debrepomanager
   ```

2. **Run sync** (rebuilds metadata):
   ```bash
   debrepomanager sync
   ```

3. **Update config** (optional):
   - Remove `repositories.codenames` section
   - Remove `repositories.components` section  
   - Keep `repositories.architectures`

### Breaking Changes

- `repositories.codenames` removed (created dynamically)
- `repositories.components` removed (created dynamically)
- Config auto-detection replaces explicit path requirement
- Environment variables now supported

### Backward Compatibility

Old config files still work:
- `codenames` and `components` sections are ignored
- All other settings work as before
- No code changes needed

---

## См. также

- [README.md](README.md) - общее описание и quick start
- [ARCHITECTURE.md](ARCHITECTURE.md) - архитектура системы
- [config.yaml.example](config.yaml.example) - шаблон конфигурации с комментариями

