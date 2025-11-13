#!/bin/bash
# Script to create test .deb packages using fpm

set -e

OUTPUT_DIR="${1:-/tmp/packages}"
mkdir -p "$OUTPUT_DIR"

# Function to create a test package
create_test_package() {
    local name="$1"
    local version="$2"
    local arch="$3"
    local codename="$4"

    echo "Creating $name $version for $arch ($codename)..."

    # Create temp directory for package content
    local tmp_dir=$(mktemp -d)

    # Create hello_world file with codename info
    mkdir -p "$tmp_dir/etc/$name"
    cat > "$tmp_dir/etc/$name/hello_world" <<EOF
Hello World from $name!
Version: $version
Architecture: $arch
Built for: $codename
EOF

    # Create package
    fpm -s dir -t deb \
        -n "$name" \
        -v "$version" \
        -a "$arch" \
        --description "Test package for $codename" \
        --maintainer "test@repomanager" \
        --license "MIT" \
        --category "utils" \
        -C "$tmp_dir" \
        --package "$OUTPUT_DIR/${name}_${version}_${arch}_${codename}.deb" \
        etc

    # Cleanup
    rm -rf "$tmp_dir"

    echo "Created: $OUTPUT_DIR/${name}_${version}_${arch}_${codename}.deb"
}

# Create test packages for different scenarios

echo "Creating test packages..."

# Same package name, different versions (for retention testing)
create_test_package "test-pkg" "1.0" "amd64" "bookworm"
create_test_package "test-pkg" "1.1" "amd64" "bookworm"
create_test_package "test-pkg" "2.0" "amd64" "bookworm"

# Same package name and version, different architectures
create_test_package "multi-arch" "1.0" "amd64" "bookworm"
create_test_package "multi-arch" "1.0" "arm64" "bookworm"

# Same package name and version, DIFFERENT content for different codenames
# This is the critical test case!
create_test_package "jethome-bsp" "1.0" "amd64" "bookworm"
create_test_package "jethome-bsp" "1.0" "amd64" "noble"

# Tool packages
create_test_package "jethome-tool" "1.0" "amd64" "bookworm"
create_test_package "jethome-tool" "2.0" "amd64" "bookworm"

echo "All test packages created in $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR"

