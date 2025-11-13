#!/usr/bin/env bash
#
# Test script for repoadd
#
# Tests basic functionality without actually uploading packages

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOADD="$SCRIPT_DIR/repoadd"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Testing repoadd script..."
echo ""

# Test 1: Check script exists and is executable
echo -n "Test 1: Script exists and executable... "
if [ -x "$REPOADD" ]; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    echo "Script not found or not executable: $REPOADD"
    exit 1
fi

# Test 2: Test help/usage
echo -n "Test 2: Help message... "
if "$REPOADD" 2>&1 | grep -q "Usage:"; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# Test 3: Test invalid environment
echo -n "Test 3: Invalid environment detection... "
if ! "$REPOADD" invalid bookworm /tmp 2>&1 | grep -q "Invalid environment"; then
    echo -e "${RED}FAIL${NC}"
    exit 1
else
    echo -e "${GREEN}PASS${NC}"
fi

# Test 4: Test invalid codename
echo -n "Test 4: Invalid codename detection... "
if ! "$REPOADD" stable "INVALID@#$" /tmp 2>&1 | grep -q "Invalid codename"; then
    echo -e "${RED}FAIL${NC}"
    exit 1
else
    echo -e "${GREEN}PASS${NC}"
fi

# Test 5: Test non-existent directory
echo -n "Test 5: Non-existent directory detection... "
if ! "$REPOADD" stable bookworm /nonexistent/path 2>&1 | grep -q "not found"; then
    echo -e "${RED}FAIL${NC}"
    exit 1
else
    echo -e "${GREEN}PASS${NC}"
fi

# Test 6: Test empty directory
echo -n "Test 6: Empty directory detection... "
TEMP_DIR=$(mktemp -d)
if ! "$REPOADD" stable bookworm "$TEMP_DIR" 2>&1 | grep -q "No .deb files found"; then
    echo -e "${RED}FAIL${NC}"
    rmdir "$TEMP_DIR"
    exit 1
else
    echo -e "${GREEN}PASS${NC}"
fi
rmdir "$TEMP_DIR"

# Test 7: Test dry-run mode with fake packages
echo -n "Test 7: Dry-run mode... "
TEMP_DIR=$(mktemp -d)
touch "$TEMP_DIR/test1.deb"
touch "$TEMP_DIR/test2.deb"

# Check if debrepomanager is available
if ! command -v debrepomanager &> /dev/null; then
    echo -e "${YELLOW}SKIP${NC} (debrepomanager not installed)"
else
    if DRY_RUN=1 "$REPOADD" stable bookworm "$TEMP_DIR" 2>&1 | grep -q "DRY RUN"; then
        echo -e "${GREEN}PASS${NC}"
    else
        echo -e "${RED}FAIL${NC}"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
fi

rm -rf "$TEMP_DIR"

# Test 8: Test explicit component parameter
echo -n "Test 8: Explicit component parameter... "
TEMP_DIR=$(mktemp -d)
touch "$TEMP_DIR/test1.deb"

if ! command -v debrepomanager &> /dev/null; then
    echo -e "${YELLOW}SKIP${NC} (debrepomanager not installed)"
else
    if DRY_RUN=1 "$REPOADD" stable bookworm "$TEMP_DIR" jethome-custom 2>&1 | grep -q "jethome-custom"; then
        echo -e "${GREEN}PASS${NC}"
    else
        echo -e "${RED}FAIL${NC}"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
fi

rm -rf "$TEMP_DIR"

# Test 9: Test 4-argument format
echo -n "Test 9: Four argument format... "
TEMP_DIR=$(mktemp -d)
touch "$TEMP_DIR/test1.deb"

if DRY_RUN=1 "$REPOADD" stable bookworm "$TEMP_DIR" my-component 2>&1 | grep -q "my-component"; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}All tests passed!${NC}"
echo ""
echo "To test actual functionality, run:"
echo "  1. Install debrepomanager: pip install -e ."
echo "  2. Create test packages directory"
echo "  3. Run: DRY_RUN=1 ./repoadd stable bookworm /path/to/packages"

