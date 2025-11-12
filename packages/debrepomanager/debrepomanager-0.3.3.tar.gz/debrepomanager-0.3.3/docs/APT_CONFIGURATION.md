# APT Configuration Examples

Примеры настройки apt репозиториев для клиентских систем.

## URL Structure

### Новый формат (Current)

Репозитории доступны по схеме:
```
http://repo.site.com/{codename}/{component}
```

Где:
- `{codename}` - кодовое имя дистрибутива (bookworm, noble, trixie, jammy)
- `{component}` - компонент репозитория (jethome-tools, jethome-armbian, jethome-bookworm)

### Старый формат (Legacy)

Для обратной совместимости поддерживается старый формат:
```
http://repo.site.com [codename] [component]
```

**Пример:**
```bash
# Старый формат (все еще работает)
deb http://repo.site.com bookworm jethome-bookworm

# Новый формат (рекомендуется)
deb http://repo.site.com/bookworm jethome-bookworm main
```

📖 **См. [DUAL_FORMAT.md](DUAL_FORMAT.md) для настройки одновременного доступа по обоим форматам**

## Debian-based Systems

### Debian 12 (Bookworm)

**Файл**: `/etc/apt/sources.list.d/jethome.list`

```bash
# JetHome Tools - утилиты и программы общего назначения
deb http://repo.site.com/bookworm jethome-tools main

# JetHome Armbian - пакеты поддержки Armbian
deb http://repo.site.com/bookworm jethome-armbian main

# JetHome Bookworm - BSP пакеты для устройств JetHome
deb http://repo.site.com/bookworm jethome-bookworm main
```

### Debian 13 (Trixie)

**Файл**: `/etc/apt/sources.list.d/jethome.list`

```bash
# JetHome Tools
deb http://repo.site.com/trixie jethome-tools main

# JetHome Armbian
deb http://repo.site.com/trixie jethome-armbian main

# JetHome BSP для Trixie
deb http://repo.site.com/trixie jethome-trixie main
```

## Ubuntu-based Systems

### Ubuntu 24.04 LTS (Noble Numbat)

**Файл**: `/etc/apt/sources.list.d/jethome.list`

```bash
# JetHome Tools
deb http://repo.site.com/noble jethome-tools main

# JetHome Armbian
deb http://repo.site.com/noble jethome-armbian main

# JetHome BSP для Noble
deb http://repo.site.com/noble jethome-noble main
```

### Ubuntu 22.04 LTS (Jammy Jellyfish)

**Файл**: `/etc/apt/sources.list.d/jethome.list`

```bash
# JetHome Tools
deb http://repo.site.com/jammy jethome-tools main

# JetHome Armbian
deb http://repo.site.com/jammy jethome-armbian main

# JetHome BSP для Jammy
deb http://repo.site.com/jammy jethome-noble main
```

## Armbian Systems

### Armbian на базе Debian Bookworm

**Файл**: `/etc/apt/sources.list.d/jethome.list`

```bash
# Основные компоненты JetHome для Armbian
deb http://repo.site.com/bookworm jethome-armbian main
deb http://repo.site.com/bookworm jethome-tools main
deb http://repo.site.com/bookworm jethome-bookworm main
```

### Armbian на базе Ubuntu Noble

**Файл**: `/etc/apt/sources.list.d/jethome.list`

```bash
# Основные компоненты JetHome для Armbian
deb http://repo.site.com/noble jethome-armbian main
deb http://repo.site.com/noble jethome-tools main
deb http://repo.site.com/noble jethome-noble main
```

## Installation Steps

### 1. Import GPG Key

```bash
# Download and import GPG key
wget -qO - http://repo.site.com/pubkey.gpg | \
    sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/jethome.gpg

# Verify key imported
gpg --no-default-keyring \
    --keyring /etc/apt/trusted.gpg.d/jethome.gpg \
    --list-keys
```

### 2. Add Repository

```bash
# Determine your system codename
CODENAME=$(lsb_release -sc)
echo "Detected codename: $CODENAME"

# Create repository file
sudo tee /etc/apt/sources.list.d/jethome.list <<EOF
deb http://repo.site.com/$CODENAME jethome-tools main
deb http://repo.site.com/$CODENAME jethome-armbian main
EOF
```

### 3. Update Package List

```bash
sudo apt update
```

### 4. Install Packages

```bash
# Install specific package
sudo apt install jethome-package-name

# Search available packages
apt search jethome

# Show package information
apt show jethome-package-name
```

## Component Descriptions

### jethome-tools
**Содержимое**: Утилиты и программы общего назначения, не специфичные для конкретного устройства

**Примеры пакетов**:
- Инструменты разработки
- Системные утилиты
- Общие библиотеки

**Кому нужен**: Всем пользователям JetHome

### jethome-armbian
**Содержимое**: Пакеты поддержки Armbian, копии из официального репозитория Armbian

**Примеры пакетов**:
- armbian-config
- armbian-firmware
- armbian-tools

**Кому нужен**: Пользователям Armbian на устройствах JetHome

### jethome-{codename} (BSP)
**Содержимое**: Board Support Package - пакеты специфичные для устройств JetHome

**Примеры пакетов**:
- Device tree overlays
- Драйвера устройств
- Firmware
- Конфигурационные пакеты

**Кому нужен**: Владельцам конкретных устройств JetHome

## Architecture Support

Все компоненты поддерживают следующие архитектуры:
- `amd64` - x86_64 (Intel/AMD 64-bit)
- `arm64` - ARMv8 (64-bit ARM)
- `riscv64` - RISC-V 64-bit

APT автоматически выбирает пакеты для архитектуры вашей системы.

## Multi-Architecture Example

Если нужны пакеты для другой архитектуры (например, cross-compilation):

```bash
# Add foreign architecture
sudo dpkg --add-architecture arm64

# Update
sudo apt update

# Install package for specific architecture
sudo apt install package-name:arm64
```

## Complete Setup Script

```bash
#!/bin/bash
# Complete JetHome repository setup

set -e

# Detect system
CODENAME=$(lsb_release -sc)
echo "Setting up JetHome repository for: $CODENAME"

# Import GPG key
echo "Importing GPG key..."
wget -qO - http://repo.site.com/pubkey.gpg | \
    sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/jethome.gpg

# Add repository
echo "Adding repository..."
sudo tee /etc/apt/sources.list.d/jethome.list <<EOF
# JetHome Repositories for $CODENAME
deb http://repo.site.com/$CODENAME jethome-tools main
deb http://repo.site.com/$CODENAME jethome-armbian main
deb http://repo.site.com/$CODENAME jethome-$CODENAME main
EOF

# Update package list
echo "Updating package list..."
sudo apt update

echo "Setup complete!"
echo "You can now install JetHome packages with: sudo apt install <package-name>"
```

## Verification

### Check Repository Configuration

```bash
# List configured repositories
grep -r "repo.site.com" /etc/apt/sources.list /etc/apt/sources.list.d/

# Check if repository is accessible
apt-cache policy | grep jethome
```

### Check Available Packages

```bash
# List all packages from JetHome repositories
apt-cache search jethome

# Show package details
apt show jethome-package-name

# List installed JetHome packages
dpkg -l | grep jethome
```

## Troubleshooting

### GPG Key Errors

```bash
# Error: NO_PUBKEY
# Re-import GPG key
wget -qO - http://repo.site.com/pubkey.gpg | \
    sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/jethome.gpg
sudo apt update
```

### Repository Not Found

```bash
# Check codename
lsb_release -sc

# Verify URL is accessible
curl -I http://repo.site.com/$(lsb_release -sc)/jethome-tools/dists/jethome-tools/Release

# Check /etc/apt/sources.list.d/jethome.list format
cat /etc/apt/sources.list.d/jethome.list
```

### Connection Issues

```bash
# Test connectivity
ping -c 3 repo.site.com

# Try with curl
curl -v http://repo.site.com/
```

## Advanced Configuration

### Using HTTPS (if available)

```bash
# Install apt-transport-https
sudo apt install apt-transport-https ca-certificates

# Update repository URL to HTTPS
deb https://repo.site.com/bookworm jethome-tools main
```

### Using Local Mirror

```bash
# If you have local mirror
deb http://local-mirror.company.lan/jethome/bookworm jethome-tools main
```

### Pin Priority

Create `/etc/apt/preferences.d/jethome` to set package priorities:

```
Package: *
Pin: origin repo.site.com
Pin-Priority: 600
```

## Docker/Container Usage

### Dockerfile Example

```dockerfile
FROM debian:bookworm

# Import GPG key
RUN wget -qO - http://repo.site.com/pubkey.gpg | \
    gpg --dearmor -o /etc/apt/trusted.gpg.d/jethome.gpg

# Add repository
RUN echo "deb http://repo.site.com/bookworm jethome-tools main" > \
    /etc/apt/sources.list.d/jethome.list

# Update and install
RUN apt update && apt install -y jethome-package

CMD ["/bin/bash"]
```

## See Also

- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [CONFIG.md](CONFIG.md) - Repository configuration
- [README.md](../README.md) - Main documentation

