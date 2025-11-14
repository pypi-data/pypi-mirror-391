# Scripts

Вспомогательные скрипты для работы с debrepomanager.

## repoadd

Упрощенный скрипт для загрузки пакетов в репозитории с поддержкой окружений stable/beta/test.

### Быстрый старт

```bash
# Загрузить пакеты в stable репозиторий
./repoadd stable bookworm armbian-bookworm

# Загрузить пакеты в beta репозиторий
./repoadd beta noble jethome-tools

# Загрузить пакеты в test репозиторий
./repoadd test bookworm ./packages/
```

### Документация

Полная документация: [REPOADD_SCRIPT.md](../docs/REPOADD_SCRIPT.md)

### Синтаксис

```bash
repoadd <stable|beta|test> <codename> <dir>
```

- `stable` → `http://deb.repo.com/`
- `beta` → `http://deb.repo.com/beta/`
- `test` → `http://deb.repo.com/test/`

### Примеры

**Загрузка в production:**
```bash
./repoadd stable bookworm armbian-bookworm
```
→ `deb http://deb.repo.com/ bookworm jethome-armbian-bookworm`

**Загрузка в beta:**
```bash
./repoadd beta noble jethome-tools
```
→ `deb http://deb.repo.com/beta/ noble jethome-tools`

**Dry-run режим:**
```bash
DRY_RUN=1 ./repoadd stable bookworm armbian-bookworm
```

### Установка

1. Убедитесь что debrepomanager установлен:
   ```bash
   pip install debrepomanager
   ```

2. Сделайте скрипт исполняемым:
   ```bash
   chmod +x repoadd
   ```

3. Опционально, добавьте в PATH:
   ```bash
   sudo ln -s $(pwd)/repoadd /usr/local/bin/repoadd
   ```

## Будущие скрипты

Здесь будут размещены дополнительные утилиты для работы с репозиториями.

