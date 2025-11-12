#!/bin/bash
#
# GPG Key Migration Script for debrepomanager clients
# 
# This script helps clients migrate from old to new GPG key
# Usage: ./migrate-gpg-key.sh NEW_KEY_URL [OLD_KEY_ID]
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check arguments
if [ $# -lt 1 ]; then
    error "Usage: $0 NEW_KEY_URL [OLD_KEY_ID]"
    echo ""
    echo "Examples:"
    echo "  $0 https://repo.example.com/gpg/new-key.asc"
    echo "  $0 https://repo.example.com/gpg/new-key.asc OLDKEY123"
    exit 1
fi

NEW_KEY_URL="$1"
OLD_KEY_ID="${2:-}"

info "GPG Key Migration for debrepomanager repositories"
echo ""

# Detect system
if [ -f /etc/debian_version ]; then
    info "Detected: Debian/Ubuntu system"
    PKG_MANAGER="apt-get"
elif [ -f /etc/redhat-release ]; then
    info "Detected: RedHat/CentOS system"
    PKG_MANAGER="yum"
else
    warn "Unknown system, assuming Debian-based"
    PKG_MANAGER="apt-get"
fi

# Download new key
info "Downloading new GPG key from: $NEW_KEY_URL"
TMP_KEY="/tmp/new-gpg-key-$$.asc"

if ! curl -fsSL "$NEW_KEY_URL" -o "$TMP_KEY"; then
    error "Failed to download GPG key"
    exit 1
fi

info "✓ Key downloaded to $TMP_KEY"

# Import new key
info "Importing new GPG key..."
if ! apt-key add "$TMP_KEY" 2>/dev/null && ! gpg --import "$TMP_KEY" 2>/dev/null; then
    error "Failed to import GPG key"
    rm -f "$TMP_KEY"
    exit 1
fi

info "✓ New GPG key imported"

# Remove old key if specified
if [ -n "$OLD_KEY_ID" ]; then
    warn "Removing old GPG key: $OLD_KEY_ID"
    
    if apt-key del "$OLD_KEY_ID" 2>/dev/null || gpg --batch --yes --delete-keys "$OLD_KEY_ID" 2>/dev/null; then
        info "✓ Old GPG key removed"
    else
        warn "Failed to remove old key (may not exist or no permissions)"
    fi
fi

# Cleanup
rm -f "$TMP_KEY"

# Update package lists
info "Updating package lists..."
if sudo $PKG_MANAGER update; then
    info "✓ Package lists updated successfully"
else
    error "Failed to update package lists"
    error "This may indicate an issue with the new key"
    exit 1
fi

# Success
echo ""
info "✅ GPG key migration completed successfully!"
echo ""
info "Next steps:"
echo "  1. Test package installation: sudo apt-get install <package>"
echo "  2. If issues occur, check /var/log/apt/term.log"
echo "  3. Contact repository administrator if problems persist"
echo ""

# Optional rollback instructions
if [ -n "$OLD_KEY_ID" ]; then
    warn "Rollback instructions (if needed):"
    echo "  1. Re-import old key"
    echo "  2. Remove new key"
    echo "  3. Run: sudo $PKG_MANAGER update"
fi
