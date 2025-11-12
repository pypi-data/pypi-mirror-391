# Dockerfile for integration testing with real aptly
FROM debian:bookworm-slim

# Install aptly, gpg, fpm, apt utils
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    apt-utils \
    ruby \
    ruby-dev \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    python3-apt \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install aptly
RUN wget -qO - https://www.aptly.info/pubkey.txt | gpg --dearmor > /etc/apt/trusted.gpg.d/aptly.gpg && \
    echo "deb http://repo.aptly.info/ squeeze main" > /etc/apt/sources.list.d/aptly.list && \
    apt-get update && \
    apt-get install -y aptly && \
    rm -rf /var/lib/apt/lists/*

# Install fpm for creating test packages
RUN gem install --no-document fpm

# Create GPG key for testing (non-interactive)
# Using test@debrepomanager as per project requirements
RUN gpg --batch --gen-key <<EOF
%no-protection
Key-Type: RSA
Key-Length: 2048
Name-Real: RepManager Test Key
Name-Email: test@debrepomanager
Expire-Date: 0
%commit
EOF

# Export GPG key ID for tests
RUN echo "export GPG_TEST_KEY_ID=$(gpg --list-secret-keys --with-colons test@debrepomanager | grep ^sec | cut -d: -f5)" >> /etc/profile.d/gpg-test.sh

# Create working directories
RUN mkdir -p /opt/debrepomanager /srv/aptly /srv/repo/public /tmp/packages

# Set working directory
WORKDIR /opt/debrepomanager

# Copy requirements and install
COPY requirements.txt setup.py pyproject.toml ./
COPY debrepomanager/ ./debrepomanager/

RUN pip3 install --break-system-packages -e ".[dev]"

# Copy tests
COPY tests/ ./tests/

# Create test packages script
COPY tests/integration/create_test_packages.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/create_test_packages.sh

CMD ["/bin/bash"]

