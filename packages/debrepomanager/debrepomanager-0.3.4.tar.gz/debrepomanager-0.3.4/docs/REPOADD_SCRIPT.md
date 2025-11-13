# repoadd Script Documentation

Скрипт для упрощенной загрузки пакетов в Debian репозиторий с поддержкой окружений stable/beta/test.

## Описание

`repoadd` - это wrapper-скрипт вокруг `debrepomanager`, который упрощает загрузку пакетов в репозитории для разных окружений (stable, beta, test).

## Синтаксис

```bash
repoadd <stable|beta|test> <codename> <dir> [component]
```

### Параметры

1. **`<stable|beta|test>`** - Окружение репозитория
   - `stable` - production репозиторий → `http://deb.repo.com/`
   - `beta` - beta-тестирование → `http://deb.repo.com/beta/`
   - `test` - тестовый репозиторий → `http://deb.repo.com/test/`

2. **`<codename>`** - Кодовое имя дистрибутива
   - Примеры: `bookworm`, `noble`, `trixie`, `jammy`

3. **`<dir>`** - Директория с .deb пакетами
   - Сканируется рекурсивно (включая подпапки)

4. **`[component]`** - Опционально: явное указание component
   - Если не указан, автоматически генерируется из имени директории
   - Позволяет точно контролировать имя компонента

## Формирование component

### Автоматическое формирование

Если component не указан явно, он формируется на основе имени директории:
- Если имя начинается с `jethome-`, используется как есть
- Иначе добавляется префикс `jethome-`

Примеры:
- `armbian-bookworm` → `jethome-armbian-bookworm`
- `jethome-tools` → `jethome-tools`
- `packages` → `jethome-packages`

### Явное указание

Можно указать component явно как 4-й параметр:

```bash
./repoadd stable bookworm ./packages/ jethome-custom
```

Это полезно когда:
- Нужно точно контролировать имя компонента
- Имя директории не подходит для component
- Один набор пакетов загружается в разные компоненты

## Примеры использования

### Пример 1: Загрузка в stable репозиторий

```bash
./repoadd stable bookworm armbian-bookworm
```

**Результат:**
- Пакеты загружаются в репозиторий `jethome-armbian-bookworm`
- Доступно по URL: `http://deb.repo.com/`
- APT конфигурация:
  ```
  deb http://deb.repo.com/ bookworm jethome-armbian-bookworm
  ```

### Пример 2: Загрузка в beta репозиторий

```bash
./repoadd beta noble jethome-tools
```

**Результат:**
- Пакеты загружаются в репозиторий `jethome-jethome-tools` (префикс не дублируется)
- Доступно по URL: `http://deb.repo.com/beta/`
- APT конфигурация:
  ```
  deb http://deb.repo.com/beta/ noble jethome-tools
  ```

### Пример 3: Загрузка в test репозиторий

```bash
./repoadd test bookworm ./packages/
```

**Результат:**
- Пакеты загружаются из директории `./packages/`
- Component: `jethome-packages`
- Доступно по URL: `http://deb.repo.com/test/`
- APT конфигурация:
  ```
  deb http://deb.repo.com/test/ bookworm jethome-packages
  ```

### Пример 4: Явное указание component

```bash
./repoadd stable bookworm ./my-packages/ jethome-custom-tools
```

**Результат:**
- Пакеты загружаются из директории `./my-packages/`
- Component: `jethome-custom-tools` (явно указан, игнорирует имя директории)
- Доступно по URL: `http://deb.repo.com/`
- APT конфигурация:
  ```
  deb http://deb.repo.com/ bookworm jethome-custom-tools
  ```

### Пример 5: Разные компоненты для одного набора пакетов

```bash
# Загрузить в stable
./repoadd stable bookworm ./build/packages/ jethome-tools

# Загрузить те же пакеты в beta для тестирования
./repoadd beta bookworm ./build/packages/ jethome-tools-beta
```

## Автоматическое создание репозитория

Скрипт автоматически создает репозиторий, если он еще не существует:

1. Проверяет существование репозитория
2. Если не существует - создает с помощью `debrepomanager create-repo`
3. Загружает пакеты

## Переменные окружения

### REPOMANAGER_CONFIG

Путь к конфигурационному файлу `debrepomanager`.

```bash
export REPOMANAGER_CONFIG=/path/to/config.yaml
./repoadd stable bookworm armbian-bookworm
```

**По умолчанию:** `/etc/debrepomanager/config.yaml`

**Примечание (v0.2+):** debrepomanager автоматически определяет конфиг из стандартных путей:
- `/etc/debrepomanager/config.yaml`
- `~/.debrepomanager/config.yaml`
- `./config.yaml`

### DRY_RUN

Режим симуляции - показывает что будет сделано, но не выполняет изменения.

```bash
DRY_RUN=1 ./repoadd stable bookworm armbian-bookworm
```

### DEBUG

Включает verbose режим для детальной диагностики.

```bash
DEBUG=1 ./repoadd stable bookworm armbian-bookworm
```

## Выход и коды ошибок

Скрипт завершается с кодом 0 при успехе, и ненулевым кодом при ошибке:
- `1` - Ошибка валидации параметров или выполнения
- `0` - Успешное выполнение

## Требования

1. **debrepomanager** должен быть установлен и доступен в PATH
   ```bash
   pip install debrepomanager
   # или
   pip install -e .
   ```

2. **Права доступа** к директориям aptly и publish
   - `/srv/aptly/` - для хранения репозиториев
   - `/srv/repo/public/` - для публикации

3. **GPG ключ** настроен в конфигурации

## Конфигурация для окружений

Для поддержки разных окружений (stable/beta/test) необходимо настроить nginx или другой веб-сервер:

### Nginx пример

```nginx
server {
    listen 80;
    server_name deb.repo.com;
    root /srv/repo/public;

    # Stable (root)
    location / {
        autoindex on;
    }

    # Beta
    location /beta/ {
        alias /srv/repo/public-beta/;
        autoindex on;
    }

    # Test
    location /test/ {
        alias /srv/repo/public-test/;
        autoindex on;
    }
}
```

### Config.yaml для окружений

Можно использовать разные конфигурационные файлы:

**config-stable.yaml:**
```yaml
aptly:
  root_base: "/srv/aptly/stable"
  publish_base: "/srv/repo/public"
```

**config-beta.yaml:**
```yaml
aptly:
  root_base: "/srv/aptly/beta"
  publish_base: "/srv/repo/public-beta"
```

**config-test.yaml:**
```yaml
aptly:
  root_base: "/srv/aptly/test"
  publish_base: "/srv/repo/public-test"
```

Использование:
```bash
REPOMANAGER_CONFIG=/etc/repomanager/config-beta.yaml \
    ./repoadd beta noble jethome-tools
```

## Workflow интеграция

### GitHub Actions пример

```yaml
name: Upload to Repository

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - stable
          - beta
          - test
      codename:
        description: 'Distribution codename'
        required: true
      package_dir:
        description: 'Package directory'
        required: true

jobs:
  upload:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Upload packages
        run: |
          ./scripts/repoadd \
            ${{ inputs.environment }} \
            ${{ inputs.codename }} \
            ${{ inputs.package_dir }}
```

## Troubleshooting

### Проблема: "debrepomanager command not found"

**Решение:**
```bash
# Установите debrepomanager
pip install debrepomanager

# Или добавьте в PATH
export PATH=$PATH:/path/to/venv/bin
```

### Проблема: "No .deb files found"

**Решение:**
```bash
# Проверьте содержимое директории
find /path/to/dir -name "*.deb"

# Убедитесь что путь правильный
ls -la /path/to/dir
```

### Проблема: "Repository creation failed"

**Решение:**
```bash
# Проверьте права доступа
ls -la /srv/aptly/
ls -la /srv/repo/public/

# Проверьте GPG ключ
gpg --list-secret-keys

# Проверьте конфигурацию
cat /etc/debrepomanager/config.yaml
```

### Проблема: "Permission denied"

**Решение:**
```bash
# Дайте права на директории
sudo chown -R $USER:$USER /srv/aptly/
sudo chown -R $USER:$USER /srv/repo/public/

# Или запустите с sudo (не рекомендуется)
sudo ./repoadd stable bookworm armbian-bookworm
```

## Безопасность

1. **Не запускайте с sudo** без необходимости
2. **Проверяйте пакеты** перед загрузкой
3. **Используйте DRY_RUN** для проверки команд
4. **Ограничьте доступ** к скрипту нужным пользователям

```bash
# Установите права
chmod 750 /path/to/repoadd
chown root:repomanager /path/to/repoadd
```

## Логирование

Скрипт выводит цветные логи:
- 🟢 **[INFO]** - информационные сообщения
- 🟡 **[WARN]** - предупреждения
- 🔴 **[ERROR]** - ошибки

Для сохранения в файл (без цветов):
```bash
./repoadd stable bookworm armbian-bookworm 2>&1 | tee upload.log
```

## См. также

- [debrepomanager README](../README.md)
- [QUICKSTART](QUICKSTART.md)
- [DEPLOYMENT_GUIDE](DEPLOYMENT_GUIDE.md)
- [APT_CONFIGURATION](APT_CONFIGURATION.md)

