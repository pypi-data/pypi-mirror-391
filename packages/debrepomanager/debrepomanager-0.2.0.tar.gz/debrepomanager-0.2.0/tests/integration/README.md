# Integration Tests

Docker-based integration tests с реальным aptly для проверки end-to-end функциональности.

## Что тестируем

### Критические сценарии:
1. ✅ **Repository Creation** - создание репозиториев работает
2. ✅ **Multi-Codename Isolation** - пакеты с одинаковым названием/версией но разным содержимым работают в разных codenames (multi-root решение)
3. ✅ **Force Recreation** - --force опция работает
4. 🔄 **Package Addition** - добавление пакетов и snapshots (Step 2.2)
5. 🔄 **APT Installation** - apt может установить пакеты из созданного репо
6. 🔄 **Dual Format** - оба формата URL работают (Step 5.1)

## Требования

- Docker (with Compose v2)
- `docker compose` command (NOT `docker-compose`)

## Quick Start

### Запуск всех integration тестов

```bash
# Из корня проекта
cd tests/integration
docker compose up --build --abort-on-container-exit

# Или через Makefile
make test-integration
```

### Запуск конкретного теста

```bash
docker compose run --rm debrepomanager-test \
    pytest tests/integration/test_integration.py::TestRepositoryCreation::test_create_repository -v
```

### Интерактивная отладка

```bash
# Запустить контейнер с shell
docker compose run --rm debrepomanager-test /bin/bash

# Внутри контейнера:
cd /opt/debrepomanager

# Создать тестовые пакеты
create_test_packages.sh /tmp/packages

# Запустить тесты
pytest tests/integration/ -v -m integration

# Проверить aptly вручную
aptly repo list
```

## Структура

```
tests/integration/
├── Dockerfile                  # Docker image с aptly, fpm, python
├── docker-compose.yml          # Compose setup (test container + nginx + apt client)
├── create_test_packages.sh     # Скрипт создания test .deb пакетов
├── test_integration.py         # Интеграционные тесты
└── README.md                   # Этот файл
```

## Docker Services

### debrepomanager-test
- Основной контейнер для запуска тестов
- Установлен aptly, fpm, python3, debrepomanager
- GPG ключ для тестирования
- Volumes: aptly root, repo publish

### repo-server (nginx)
- HTTP сервер для созданных репозиториев
- Доступен на http://localhost:8080
- Volume: /srv/repo (read-only)

### apt-client (debian:bookworm)
- Клиент для проверки установки пакетов
- Может добавить репозиторий и установить пакеты
- Доступ к repo-server по сети

## Test Packages

Создаются через fpm:

```bash
# jethome-bsp v1.0 для bookworm (содержимое: "BSP for bookworm")
jethome-bsp_1.0_amd64_bookworm.deb

# jethome-bsp v1.0 для noble (содержимое: "BSP for noble")
jethome-bsp_1.0_amd64_noble.deb  # SAME name/version, DIFFERENT content!

# jethome-tool для разных версий
jethome-tool_1.0_amd64_bookworm.deb
jethome-tool_2.0_amd64_noble.deb
```

**Критический тест**: `jethome-bsp v1.0` существует для bookworm и noble с РАЗНЫМ содержимым.
Это работает благодаря multi-root (изоляция pools).

## Test Markers

```python
@pytest.mark.integration  # Все integration тесты
@pytest.mark.slow         # Долгие тесты (с apt install)
```

### Запуск только unit тестов (без integration)

```bash
pytest -m "not integration"
```

### Запуск только integration тестов

```bash
pytest -m integration
```

## CI Integration

В GitHub Actions (`.github/workflows/tests.yml`):

```yaml
integration:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Run integration tests
      run: |
        cd tests/integration
        docker compose up --build --abort-on-container-exit
```

## Troubleshooting

### Docker build fails

```bash
# Rebuild without cache
docker compose build --no-cache
```

### GPG key issues

```bash
# Check GPG keys in container
docker compose run --rm debrepomanager-test gpg --list-secret-keys
```

### Aptly issues

```bash
# Interactive shell
docker compose run --rm debrepomanager-test /bin/bash

# Check aptly
aptly version
aptly repo list
```

### Permission issues

```bash
# Fix volumes permissions
docker compose down -v
docker compose up --build
```

## Cleanup

```bash
# Stop and remove containers, volumes
docker compose down -v

# Remove images
docker compose down --rmi all -v
```

## Development Workflow

1. **Разработка кода** → unit тесты (моки)
2. **Before commit** → `make check-all` (unit tests)
3. **After commit** → integration tests (Docker)
4. **Before release** → полный набор integration + manual testing

## See Also

- [docs/DEVELOPMENT.md](../../docs/DEVELOPMENT.md) - Development guide
- [.github/workflows/tests.yml](../../.github/workflows/tests.yml) - CI configuration
- [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) - Architecture overview

