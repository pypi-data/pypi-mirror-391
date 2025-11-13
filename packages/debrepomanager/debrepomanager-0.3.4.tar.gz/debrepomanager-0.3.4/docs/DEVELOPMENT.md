# Development Guide

Руководство для разработчиков Debian Repository Manager.

## Быстрый старт

### Настройка окружения

```bash
# Клонирование репозитория
git clone https://github.com/jethome/repomanager.git
cd repomanager

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей (включая dev)
pip install -r requirements.txt

# Установка в режиме разработки
pip install -e .
```

### Структура проекта

```
repomanager/
├── repomanager/          # Основной пакет
│   ├── __init__.py       # Package initialization
│   ├── cli.py            # CLI interface (argparse/click)
│   ├── config.py         # Configuration management
│   ├── aptly.py          # Aptly wrapper
│   ├── retention.py      # Retention policy logic
│   ├── gpg.py            # GPG operations
│   └── utils.py          # Utility functions
├── tests/                # Тесты
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_aptly.py
│   ├── test_retention.py
│   └── test_gpg.py
├── .github/workflows/    # GitHub Actions
├── docs/                 # Дополнительная документация (будет создана)
├── config.yaml.example   # Пример конфигурации
├── requirements.txt      # Python dependencies
├── setup.py              # Installation script
└── README.md             # Main documentation
```

## Разработка

### Code Style

Проект следует PEP 8 с использованием следующих инструментов:

#### Black (форматирование)

```bash
# Отформатировать весь код
black repomanager/

# Проверить без изменений
black --check repomanager/

# Для отдельного файла
black repomanager/cli.py
```

**Настройки** (pyproject.toml):
```toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
```

#### Flake8 (линтинг)

```bash
# Проверить весь код
flake8 repomanager/

# С подробным выводом
flake8 --show-source repomanager/
```

**Настройки** (.flake8):
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist,venv
```

#### MyPy (type checking)

```bash
# Проверка типов
mypy repomanager/

# Для конкретного файла
mypy repomanager/config.py
```

**Настройки** (mypy.ini):
```ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### Стиль кода

- **Отступы**: 4 пробела (не табы) - для Python файлов
- **Длина строки**: 88 символов (Black default)
- **Импорты**: сортировка через isort или вручную (stdlib → third-party → local)
- **Docstrings**: Google style
- **Type hints**: обязательны для публичных функций и методов

**Пример функции**:

```python
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def add_packages(
    codename: str,
    component: str,
    packages: List[str],
    dry_run: bool = False
) -> bool:
    """Add packages to repository.

    Args:
        codename: Distribution codename (e.g., 'bookworm')
        component: Repository component (e.g., 'jethome-tools')
        packages: List of package file paths
        dry_run: If True, don't actually add packages

    Returns:
        True if successful, False otherwise

    Raises:
        ValueError: If codename or component is invalid
        FileNotFoundError: If package files don't exist
    """
    logger.info(f"Adding {len(packages)} packages to {codename}/{component}")

    if not packages:
        raise ValueError("No packages provided")

    # Implementation...
    return True
```

## Тестирование

### Запуск тестов

```bash
# Все тесты
pytest

# С подробным выводом
pytest -v

# Конкретный файл
pytest tests/test_config.py

# Конкретный тест
pytest tests/test_config.py::test_load_config

# С покрытием
pytest --cov=repomanager --cov-report=html

# Открыть отчет о покрытии
xdg-open htmlcov/index.html
```

### Написание тестов

Используем `pytest` с `pytest-mock` для моков.

**Пример теста**:

```python
import pytest
from repomanager.config import Config


def test_load_config_default():
    """Test loading configuration with defaults."""
    config = Config()
    config.load_default()

    assert config.aptly_root_base == "/srv/aptly"
    assert config.retention_default_min_versions == 5


def test_load_config_from_file(tmp_path):
    """Test loading configuration from YAML file."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
    aptly:
      root_base: /custom/path
    """)

    config = Config()
    config.load(str(config_file))

    assert config.aptly_root_base == "/custom/path"


@pytest.fixture
def mock_aptly(mocker):
    """Mock aptly subprocess calls."""
    return mocker.patch("subprocess.run")


def test_add_packages(mock_aptly):
    """Test adding packages with mocked aptly."""
    from repomanager.aptly import AptlyManager

    manager = AptlyManager(Config())
    manager.add_packages("bookworm", "jethome-tools", ["test.deb"])

    # Verify aptly was called correctly
    mock_aptly.assert_called_once()
```

### Coverage цели

- **Минимум**: 70% покрытия
- **Цель**: 85%+ покрытия
- **Критичные модули** (config, aptly, retention): 90%+

## Отладка

### Локальное тестирование CLI

```bash
# С указанием конфига
repomanager --config config.yaml.example list

# С verbose логированием
repomanager --verbose add --codename bookworm --component test --packages test.deb

# Dry-run режим
repomanager --dry-run cleanup --codename bookworm --component test
```

### Отладка aptly операций

```bash
# Проверить что aptly установлен
which aptly
aptly version

# Создать тестовый aptly root
mkdir -p /tmp/test-aptly
export APTLY_CONFIG=/tmp/test-aptly/aptly.conf

# Создать конфиг aptly
cat > $APTLY_CONFIG <<EOF
{
  "rootDir": "/tmp/test-aptly",
  "architectures": ["amd64", "arm64"]
}
EOF

# Тестовые команды
aptly repo create -config=$APTLY_CONFIG test-repo
aptly repo list -config=$APTLY_CONFIG
```

### Debugging в Python

```python
# Добавить breakpoint
import pdb; pdb.set_trace()

# Или в Python 3.7+
breakpoint()

# Логирование для отладки
import logging
logging.basicConfig(level=logging.DEBUG)
```

## CI/CD

### GitHub Actions для разработки

`.github/workflows/tests.yml` (создать):
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -e .

    - name: Run tests
      run: pytest --cov=repomanager --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
```

## Workflow разработки

### Создание новой функции

1. **Создать ветку**:
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Написать тесты** (TDD подход):
   ```bash
   # Создать тест
   vim tests/test_new_feature.py
   # Тест должен падать
   pytest tests/test_new_feature.py
   ```

3. **Реализовать функцию**:
   ```bash
   vim repomanager/new_feature.py
   # Тест должен проходить
   pytest tests/test_new_feature.py
   ```

4. **Проверить code style**:
   ```bash
   black repomanager/
   flake8 repomanager/
   mypy repomanager/
   ```

5. **Запустить все тесты**:
   ```bash
   pytest
   ```

6. **Commit и push**:
   ```bash
   git add .
   git commit -m "Add new feature: description"
   git push origin feature/new-feature
   ```

7. **Создать Pull Request** на GitHub

### Исправление бага

1. **Создать issue** на GitHub (если еще не создан)

2. **Создать ветку**:
   ```bash
   git checkout -b fix/bug-description
   ```

3. **Написать failing test** (воспроизводит баг):
   ```bash
   vim tests/test_bugfix.py
   pytest tests/test_bugfix.py  # должен падать
   ```

4. **Исправить баг**:
   ```bash
   vim repomanager/module.py
   pytest tests/test_bugfix.py  # должен проходить
   ```

5. **Проверить что не сломали ничего другого**:
   ```bash
   pytest
   ```

6. **Commit, push, PR** (как выше)

## Релизы

### Версионирование

Используем Semantic Versioning (semver): `MAJOR.MINOR.PATCH`

- **MAJOR**: несовместимые изменения API
- **MINOR**: новая функциональность (обратно совместимая)
- **PATCH**: исправления багов

### Процесс релиза

1. **Обновить версию**:
   ```python
   # repomanager/__init__.py
   __version__ = "0.2.0"
   ```

2. **Обновить CHANGELOG.md** (создать если нет):
   ```markdown
   ## [0.2.0] - 2025-10-29
   ### Added
   - New retention policy feature
   ### Fixed
   - Bug in aptly wrapper
   ```

3. **Commit и tag**:
   ```bash
   git add repomanager/__init__.py CHANGELOG.md
   git commit -m "Release v0.2.0"
   git tag -a v0.2.0 -m "Version 0.2.0"
   git push origin main --tags
   ```

4. **GitHub Release**: создать на GitHub с описанием изменений

## Полезные ссылки

- [aptly documentation](https://www.aptly.info/doc/overview/)
- [Python Debian library](https://pypi.org/project/python-debian/)
- [Click documentation](https://click.palletsprojects.com/)
- [pytest documentation](https://docs.pytest.org/)
- [Debian Repository Format](https://wiki.debian.org/DebianRepository/Format)

## Troubleshooting

### Import errors в тестах

```bash
# Убедиться что установлен в editable mode
pip install -e .

# Или добавить в PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH
```

### Aptly не найден в тестах

Используем моки для всех внешних вызовов:
```python
@pytest.fixture
def mock_subprocess(mocker):
    return mocker.patch("subprocess.run")
```

### GPG ошибки в тестах

Моки для GPG операций:
```python
@pytest.fixture
def mock_gpg(mocker):
    mocker.patch("subprocess.run")
    mocker.patch("os.path.exists", return_value=True)
```

## Контакты

- Issues: https://github.com/jethome/repomanager/issues
- Discussions: https://github.com/jethome/repomanager/discussions
- Email: support@jethome.ru

