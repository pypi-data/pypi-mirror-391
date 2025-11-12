# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Production GitHub Actions workflows for package deployment (Phase 7)
- REST API server (optional, low priority)

## [0.3.1] - 2025-11-11

### Fixed
- **Config path consistency**: Corrected all paths to use `debrepomanager` (not `repomanager`)
  - System config: `/etc/debrepomanager/config.yaml` (was `/etc/repomanager/`)
  - User config: `~/.debrepomanager/config.yaml` (was `~/.repomanager/`)
  - Local config: `./config.yaml` (was `./repomanager.yaml` - simpler!)
- **repoadd script**: Now uses auto-detection (finds `./config.yaml` in current directory)
  - Removed hardcoded `/etc/repomanager/config.yaml` default
  - Uses debrepomanager auto-detection by default
  - Set `REPOMANAGER_CONFIG` env var to override
- **Documentation**: Updated all config path references in docs
- **Tests**: Updated test_config_v02.py for new paths

### Technical
- Consistent naming throughout: `debrepomanager` everywhere
- Local config now just `config.yaml` (easier to use)
- Total tests: 304 passed
- Coverage: 80.61%

## [0.3.0] - 2025-11-11

### Fixed
- **Retention Policy max_age_days now works!**: Upload date tracking implemented
  - Uses file modification time from aptly pool directory
  - Works for ALL packages (new and existing)
  - No additional metadata tracking needed
  - Acceptable performance for monthly cleanup operations
  - Fallback to datetime.now() if file not found

### Technical
- `retention._get_package_upload_date()` reads mtime from pool files
- Simple implementation using existing data
- No sync issues with metadata
- Total tests: 304
- Coverage: 80.76%

## [0.2.1] - 2025-11-11

### Added
- **GPG Key Rotation (Phase 9)**: Zero-downtime GPG key rotation
  - `debrepomanager rotate-gpg-key` command for safe key rotation
  - Automatic rollback on publish failure (prevents data loss)
  - Grace period support (manual process, both keys valid)
  - Rollback capability with `--rollback --old-key-id`
  - Verification mode with `--verify-only`
  - Client migration script: `scripts/migrate-gpg-key.sh`
  - Auto-detects system (Debian/Ubuntu/RedHat)
  - Comprehensive documentation in `docs/GPG_ROTATION.md`
  - 16 tests with 88% coverage for gpg_rotation.py

### Security
- **Critical safety features in GPG rotation**:
  - Automatic rollback if new key publish fails
  - Repository stays published except disaster scenario
  - CRITICAL error alerts if both publish attempts fail
  - Pre-validation of new key before rotation starts
  - Proper exception chaining for troubleshooting

### Technical
- Total tests: 304 (+16 GPG rotation tests)
- Coverage: 81.43%
- New module: `debrepomanager/gpg_rotation.py` (116 lines, 88% coverage)

## [0.2.0] - 2025-11-11

### Added
- **Retention Policy Engine**: Automatic cleanup of old package versions
  - `debrepomanager cleanup` command for package retention management
  - Configurable policies: `min_versions`, `max_age_days`, `keep_latest`, `delete_last_aged_version`
  - Per-component policy overrides
  - Safety features: `keep_latest` protects newest versions, `delete_last_aged_version` prevents complete removal
  - Dry-run mode by default (use `--apply` to actually remove packages)
  - Debian version comparison using `python-debian`
  - Comprehensive test suite (26 tests covering all scenarios)
  - Batch removal support to handle large package sets efficiently
  - ⚠️  Limitation: max_age_days not functional (upload_date tracking TODO for v0.3)
- **repoadd script**: Simplified upload script for stable/beta/test environments
  - Automatic repository creation if not exists
  - Component name auto-detection from directory name
  - **Optional explicit component parameter** - 4th argument to override auto-detection
  - Support for environment-specific configurations
  - DRY_RUN mode for testing
  - Comprehensive error handling and validation
  - Color-coded output for better readability
- **Integration tests for repoadd**: Full test suite with Docker
  - 12 integration tests covering all scenarios
  - Tests for auto-component and explicit component modes
  - Tests for all environments (stable/beta/test)
  - Dry-run mode testing
- **Environment-specific configurations**:
  - `config-stable.yaml.example` for production
  - `config-beta.yaml.example` for pre-release
  - `config-test.yaml.example` for testing
- **Documentation**:
  - `REPOADD_SCRIPT.md` - Complete usage guide
  - `NGINX_MULTI_ENV.md` - Nginx configuration for multi-environment setup
  - `scripts/README.md` - Scripts directory documentation
- **Test script**: `test_repoadd.sh` for validation

## [0.1.3] - 2025-11-03

### Changed
- **Generic example URLs**: All `repo.jethome.ru` replaced with `repo.site.com`
  - Makes documentation deployment-agnostic
  - Users can substitute their own domain
  - Generic placeholder for examples

### Technical
- Version bump to 0.1.3
- 150+ URL references updated
- No code changes, documentation only

## [0.1.2] - 2025-11-03

### Changed
- **Documentation translated to English**
  - README.md: Complete English translation for PyPI
  - Primary language: English (for international audience)
  - Russian documentation preserved in docs/ru/ (future)

### Technical
- Version bump to 0.1.2
- All user-facing documentation in English
- Improved PyPI package description

## [0.1.1] - 2025-11-03

### Changed
- **Package renamed**: `repomanager` → `debrepomanager`
  - New package name on PyPI: `debrepomanager`
  - Command name: `debrepomanager` (no alias to avoid PyPI conflicts)
  - All imports updated to `debrepomanager`
  - **Migration required**: Replace `repomanager` with `debrepomanager` in scripts
  
### Added
- **PyPI publication workflow**: Automatic publishing on releases
  - Triggered on GitHub release creation
  - Uses `PYPI_TOKEN` secret
  - Package: https://pypi.org/project/debrepomanager/
  
- **GPG Key Rotation plan**: Phase 9 added to roadmap (v1.1)
  - Zero downtime key rotation
  - Grace period support
  - Client migration tools
  - Rollback mechanism
  
- **Deployment Guide**: Complete step-by-step instructions
  - docs/DEPLOYMENT_GUIDE.md
  - Covers /opt/repo + /beta scenario
  - Automated scripts included
  - Client setup examples

### Fixed
- All workflows use self-hosted runners
- Artifacts minimized (0 uploads)
- Integration tests run on all push/PR events

### Documentation
- Git workflow rule added (NEVER push to main!)
- All cursorrules updated for v0.1.1
- 9 comprehensive reports in docs/reports/

## [0.1.0] - 2025-11-03

### Added

#### Core Functionality
- **Configuration management** (`config.py`)
  - YAML-based configuration with merging support
  - Server and repository level configs
  - Comprehensive validation
  - Support for multiple codenames, components, and architectures

- **Aptly wrapper** (`aptly.py`)
  - Multi-root architecture (isolated aptly instances per codename)
  - Repository operations: create, delete, list, verify
  - Atomic package updates via snapshots
  - Automatic snapshot cleanup (configurable retention)
  - Support for multiple architectures (amd64, arm64, riscv64)

- **GPG integration** (`gpg.py`)
  - Automatic GPG signing of all publications
  - Support for gpg-agent with passphrase caching
  - Key availability checking
  - Signing verification

- **Utilities** (`utils.py`)
  - Debian package metadata parsing (python-debian)
  - Version comparison with Debian rules (apt_pkg)
  - Recursive .deb file discovery
  - Package age calculation
  - Structured logging setup

- **CLI interface** (`cli.py`)
  - `add` - Add packages to repository with atomic updates
  - `create-repo` - Create new repository
  - `delete-repo` - Safely delete repository (with confirmation)
  - `list` - List repositories and packages
  - Global options: --config, --verbose, --dry-run
  - Progress indicators and user-friendly error messages

#### Dual Format Support
- **Backward compatibility** for old and new URL formats
  - Old format: `deb http://repo.site.com bookworm component`
  - New format: `deb http://repo.site.com/bookworm component main`
- Automatic symlink creation for old format access
- Configurable via `dual_format.enabled` and `dual_format.auto_symlink`
- Portable relative symlinks for easy repository migration

#### Documentation
- Comprehensive README with examples
- Architecture documentation (ARCHITECTURE.md)
- Implementation plan and progress tracking
- Development guide (DEVELOPMENT.md)
- Configuration reference (CONFIG.md)
- Quick start guide (QUICKSTART.md)
- APT configuration examples (APT_CONFIGURATION.md)
- Dual format technical documentation (DUAL_FORMAT.md)

#### Testing & Quality
- 181 unit tests with 93% code coverage
- Integration test infrastructure (Docker-based)
- pytest configuration with coverage enforcement
- Code quality tools: black, flake8, mypy
- Type hints throughout codebase
- Continuous integration via GitHub Actions

#### CI/CD for Development
- Automatic code review workflow
- Test execution on multiple Python versions (3.11, 3.12)
- Auto-fix workflow for code style issues
- Documentation validation
- Coverage reporting

### Features

- **Multi-distribution support**: bookworm, noble, trixie, jammy
- **Multi-architecture**: amd64, arm64, riscv64
- **Multi-component**: flexible component naming (jethome-tools, jethome-armbian, etc.)
- **Atomic updates**: zero downtime package updates via snapshots
- **Auto-create repositories**: optional automatic repository creation
- **Configurable snapshot retention**: keep last N snapshots per repository
- **Force operations**: recreate existing repositories with --force flag
- **Dry-run mode**: preview operations without making changes

### Technical Details

- Python 3.11+ required
- Dependencies: click, pyyaml, python-debian, apt_pkg (optional)
- Uses aptly for repository management
- Supports GPG signing with configurable key
- Modular architecture with clear separation of concerns

### Configuration

- YAML-based configuration file
- Default locations: `./config.yaml`, `/etc/debrepomanager/config.yaml`
- Configurable paths for aptly root and publish directories
- Per-component retention policy overrides
- GPG configuration with agent support

[Unreleased]: https://github.com/jethome/repomanager/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/jethome/repomanager/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/jethome/repomanager/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/jethome/repomanager/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/jethome/repomanager/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/jethome/repomanager/releases/tag/v0.1.0

