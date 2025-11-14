# Dual Repository Format Support

Поддержка одновременного доступа к репозиториям по двум форматам URL.

## Два формата доступа

Система поддерживает оба формата одновременно:

### Старый формат

```bash
deb http://repo.site.com bookworm jethome-bookworm
deb http://repo.site.com bookworm jethome-tools
deb http://repo.site.com bookworm jethome-armbian
```

**Структура:**
- Base URL: `http://repo.site.com`
- Distribution: `bookworm` (codename системы)
- Component: `jethome-bookworm` (название репозитория)

### Новый формат

```bash
deb http://repo.site.com/bookworm jethome-bookworm main
deb http://repo.site.com/bookworm jethome-tools main
deb http://repo.site.com/bookworm jethome-armbian main
```

**Структура:**
- Base URL: `http://repo.site.com/bookworm` (с codename в пути)
- Distribution: `jethome-bookworm` (название репозитория)
- Component: `main`

## Реализация одновременной поддержки

### Вариант 1: Symlinks (Рекомендуется)

Создаем symlinks для старого формата, указывающие на новую структуру.

**Структура на диске:**
```
/srv/repo/public/
├── bookworm/                          # Новый формат (основное хранение)
│   ├── jethome-bookworm/
│   │   ├── dists/jethome-bookworm/
│   │   │   ├── main/
│   │   │   │   ├── binary-amd64/
│   │   │   │   ├── binary-arm64/
│   │   │   │   └── binary-riscv64/
│   │   │   └── Release
│   │   └── pool/
│   │       └── main/
│   ├── jethome-tools/
│   │   ├── dists/jethome-tools/
│   │   └── pool/
│   └── jethome-armbian/
│       ├── dists/jethome-armbian/
│       └── pool/
│
└── dists/                             # Старый формат (symlinks)
    └── bookworm/
        ├── jethome-bookworm/ -> ../../bookworm/jethome-bookworm/dists/jethome-bookworm
        ├── jethome-tools/ -> ../../bookworm/jethome-tools/dists/jethome-tools
        └── jethome-armbian/ -> ../../bookworm/jethome-armbian/dists/jethome-armbian
```

**Создание symlinks:**
```bash
#!/bin/bash
# create-dual-format-structure.sh

PUBLISH_BASE="/srv/repo/public"
CODENAME="bookworm"
COMPONENTS=("jethome-bookworm" "jethome-tools" "jethome-armbian")

# Создать директорию для старого формата
mkdir -p "$PUBLISH_BASE/dists/$CODENAME"

# Создать symlinks для каждого компонента
for component in "${COMPONENTS[@]}"; do
    NEW_PATH="$PUBLISH_BASE/$CODENAME/$component/dists/$component"
    OLD_PATH="$PUBLISH_BASE/dists/$CODENAME/$component"

    # Относительный путь
    RELATIVE_PATH="../../$CODENAME/$component/dists/$component"

    # Создать symlink
    ln -sf "$RELATIVE_PATH" "$OLD_PATH"

    echo "Created symlink: $OLD_PATH -> $RELATIVE_PATH"
done

echo "Done! Both formats are now supported."
```

**Применение для всех codenames:**
```bash
#!/bin/bash
# setup-dual-format-all.sh

PUBLISH_BASE="/srv/repo/public"
CODENAMES=("bookworm" "noble" "trixie" "jammy")
COMPONENTS=("jethome-tools" "jethome-armbian")

for codename in "${CODENAMES[@]}"; do
    mkdir -p "$PUBLISH_BASE/dists/$codename"

    for component in "${COMPONENTS[@]}"; do
        # Динамический компонент для BSP
        bsp_component="jethome-$codename"

        # Symlinks для стандартных компонентов
        ln -sf "../../$codename/$component/dists/$component" \
               "$PUBLISH_BASE/dists/$codename/$component"

        # Symlink для BSP компонента
        ln -sf "../../$codename/$bsp_component/dists/$bsp_component" \
               "$PUBLISH_BASE/dists/$codename/$bsp_component"
    done

    echo "Setup complete for $codename"
done
```

### Вариант 2: Nginx Rewrite

Использование nginx для автоматического rewrite старого формата на новый.

**Конфигурация nginx:**
```nginx
server {
    listen 80;
    server_name repo.site.com;
    root /srv/repo/public;

    # Новый формат - прямой доступ
    location ~ ^/([^/]+)/([^/]+)/ {
        try_files $uri $uri/ =404;
    }

    # Старый формат - rewrite на новый
    # /dists/bookworm/jethome-tools/ -> /bookworm/jethome-tools/dists/jethome-tools/
    location ~ ^/dists/([^/]+)/([^/]+)/(.*)$ {
        rewrite ^/dists/([^/]+)/([^/]+)/(.*)$ /$1/$2/dists/$2/$3 last;
    }

    # Pool доступ (оба формата)
    location ~ ^/pool/ {
        try_files $uri $uri/ =404;
    }

    location / {
        autoindex on;
    }

    # Кеширование метаданных
    location ~ /(Release|Packages|Sources)(\.gz|\.bz2|\.xz)?$ {
        expires 1h;
        add_header Cache-Control "public, must-revalidate";
    }
}
```

### Вариант 3: Dual Publish (Aptly)

Публикация в оба формата одновременно на уровне aptly.

**Python реализация:**
```python
class AptlyManager:
    def publish_dual_format(
        self,
        codename: str,
        component: str,
        snapshot: str
    ) -> bool:
        """Publish in both old and new formats."""

        # Новый формат (основной)
        new_prefix = f"{codename}/{component}"
        self._run_aptly([
            "publish", "switch",
            component,              # distribution
            new_prefix,             # prefix
            snapshot
        ], codename)

        # Старый формат (если включен в конфиге)
        if self.config.dual_format_enabled:
            # Публикуем тот же snapshot в старом формате
            old_prefix = ""  # без префикса
            self._run_aptly([
                "publish", "switch",
                codename,           # distribution
                component,          # prefix (компонент как префикс)
                snapshot
            ], codename)

        return True
```

## Конфигурация

### config.yaml

```yaml
repositories:
  # Поддержка двух форматов одновременно
  dual_format:
    # Включить поддержку старого формата
    enabled: true

    # Метод реализации: symlink, nginx, dual_publish
    method: "symlink"

    # Автоматически создавать symlinks при публикации
    auto_symlink: true
```

### Автоматическое создание symlinks при публикации

```python
def publish_snapshot(
    self,
    codename: str,
    component: str,
    snapshot_name: str,
    is_initial: bool = False
) -> bool:
    """Publish with automatic dual format support."""

    # Публикация в новом формате
    prefix = f"{codename}/{component}"

    if is_initial:
        self._run_aptly([
            "publish", "snapshot",
            "-distribution", component,
            "-gpg-key", self.config.gpg_key_id,
            snapshot_name,
            prefix
        ], codename)
    else:
        self._run_aptly([
            "publish", "switch",
            component,
            prefix,
            snapshot_name
        ], codename)

    # Создать/обновить symlinks для старого формата
    if self.config.dual_format_enabled:
        self._create_format_symlinks(codename, component)

    return True

def _create_format_symlinks(self, codename: str, component: str):
    """Create symlinks for old format access."""
    import os
    from pathlib import Path

    publish_base = Path(self.config.publish_base)

    # Путь нового формата
    new_path = publish_base / codename / component / "dists" / component

    # Путь старого формата
    old_path = publish_base / "dists" / codename / component
    old_path.parent.mkdir(parents=True, exist_ok=True)

    # Относительный путь для symlink
    relative = os.path.relpath(new_path, old_path.parent)

    # Создать symlink
    if old_path.exists() and old_path.is_symlink():
        old_path.unlink()

    if not old_path.exists():
        os.symlink(relative, old_path)
        self.logger.info(f"Created symlink for old format: {old_path}")
```

## Проверка работоспособности

### Тест старого формата

```bash
# Release файл
curl -I http://repo.site.com/dists/bookworm/jethome-bookworm/Release

# Packages
curl -I http://repo.site.com/dists/bookworm/jethome-bookworm/main/binary-amd64/Packages

# Оба должны вернуть 200 OK
```

### Тест нового формата

```bash
# Release файл
curl -I http://repo.site.com/bookworm/jethome-bookworm/dists/jethome-bookworm/Release

# Packages
curl -I http://repo.site.com/bookworm/jethome-bookworm/dists/jethome-bookworm/main/binary-amd64/Packages

# Оба должны вернуть 200 OK
```

### Проверка через apt

```bash
# Старый формат
echo "deb http://repo.site.com bookworm jethome-tools" | \
    sudo tee /etc/apt/sources.list.d/test-old.list
sudo apt update

# Новый формат
echo "deb http://repo.site.com/bookworm jethome-tools main" | \
    sudo tee /etc/apt/sources.list.d/test-new.list
sudo apt update

# Оба должны работать без ошибок
```

## Сравнение методов

### Symlinks

**Преимущества:**
- ✅ Нет дублирования данных
- ✅ Простая реализация
- ✅ Прозрачно для пользователей
- ✅ Автоматическое обновление

**Недостатки:**
- ❌ Требуется поддержка symlinks в файловой системе
- ❌ Нужно создавать symlinks при каждой публикации

### Nginx Rewrite

**Преимущества:**
- ✅ Не требует изменений на диске
- ✅ Гибкая настройка
- ✅ Можно добавить логирование/мониторинг

**Недостатки:**
- ❌ Зависимость от nginx
- ❌ Небольшой overhead на rewrite

### Dual Publish

**Преимущества:**
- ✅ Полная изоляция форматов
- ✅ Независимые настройки

**Недостатки:**
- ❌ Дублирование данных на диске
- ❌ Увеличенное время публикации
- ❌ Больше места на диске

## Рекомендации

### Для production

**Используйте symlinks:**
- Оптимальный баланс простоты и эффективности
- Нет дублирования данных
- Автоматизируется в repomanager

### Веб-сервер

**Nginx конфигурация минимальная:**
```nginx
server {
    listen 80;
    server_name repo.site.com;
    root /srv/repo/public;

    location / {
        autoindex on;
    }
}
```

Symlinks будут работать прозрачно, nginx не нужно настраивать специально.

## Мониторинг (опционально)

Если хотите отслеживать какой формат используется:

```nginx
# В nginx добавить
log_format repo_format '$remote_addr "$request" format=$repo_format';

map $request_uri $repo_format {
    default "new";
    ~^/dists/ "old";
}

access_log /var/log/nginx/repo_access.log repo_format;
```

Анализ:
```bash
# Статистика использования форматов
awk '{print $NF}' /var/log/nginx/repo_access.log | \
    sort | uniq -c

# Результат примерно:
# 1523 format=new
#  842 format=old
```

## See Also

- [APT_CONFIGURATION.md](APT_CONFIGURATION.md) - Примеры для пользователей
- [ARCHITECTURE.md](ARCHITECTURE.md) - Архитектура репозиториев
- [CONFIG.md](CONFIG.md) - Конфигурация repomanager


