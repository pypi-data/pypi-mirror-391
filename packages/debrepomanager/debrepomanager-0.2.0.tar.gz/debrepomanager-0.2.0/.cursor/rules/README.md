# Cursor Rules for debrepomanager

Project-specific rules and guidelines for Cursor AI.

## 📁 Rule Structure

### Shared Rules (10 files)
Universal best practices from workspace `.cursor/` repository:

| File | Description |
|------|-------------|
| shared-code-quality.mdc | Code quality standards (SOLID, DRY, KISS) |
| shared-testing-standards.mdc | Testing requirements and best practices |
| shared-version-control.mdc | Git workflow and commit standards |
| shared-development-workflow.mdc | Development patterns and workflows |
| shared-documentation-standards.mdc | Documentation guidelines |
| shared-environment-setup.mdc | Environment and dependency management |
| shared-security-practices.mdc | Security best practices |
| shared-release-management.mdc | Version and release management |
| shared-commands-management.mdc | Command file guidelines |
| shared-rules-management.mdc | Rule organization and maintenance |

### Local Rules (7 files)
Project-specific rules for debrepomanager:

| File | Description |
|------|-------------|
| local-mvp-status.mdc | Current MVP status and progress (v0.2.0) |
| local-architecture.mdc | Module structure and dependencies |
| local-aptly.mdc | Aptly integration patterns |
| local-docker-python.mdc | Docker Compose v2 and Python 3.11+ |
| local-git-workflow.mdc | Project Git workflow |
| local-pitfalls.mdc | Common pitfalls and anti-patterns |
| local-quick-reference.mdc | Quick reference and navigation |

## 🎯 Project Overview

**debrepomanager** - Debian repository manager based on aptly with support for multiple distributions, architectures, and components.

### Key Technologies
- **Backend**: aptly (Debian repository management)
- **Language**: Python 3.11+ (tested on 3.11, 3.12, 3.13)
- **CLI**: click
- **Testing**: pytest (263 tests, 92.98% coverage)
- **Fuzzing**: Hypothesis (25 property-based tests)
- **Code Quality**: black, flake8, mypy, isort
- **Timeouts**: pytest-timeout (30s per test)

### Project Structure
```
debrepomanager/
├── docs/                    # Documentation (35+ files)
├── debrepomanager/          # Main Python package
│   ├── __init__.py         # Package exports (100%)
│   ├── config.py           # Config system (100%)
│   ├── utils.py            # Utilities (97%)
│   ├── metadata.py         # Metadata tracking (100%)
│   ├── gpg.py              # GPG signing (100%)
│   ├── aptly.py            # Aptly wrapper (88%)
│   └── cli.py              # CLI interface (87%)
├── tests/                   # Tests (263 tests)
├── .github/workflows/       # GitHub Actions (6 workflows)
├── .cursor/rules/           # Cursor rules (17 files)
└── config.yaml.example      # Configuration template
```

## 🚀 Quick Start for AI

### When Starting Development
1. **Read**: [local-mvp-status.mdc](local-mvp-status.mdc) - current status v0.2.0
2. **Check**: [docs/IMPLEMENTATION_PLAN.md](../../docs/IMPLEMENTATION_PLAN.md) - implementation plan
3. **Review**: [PROJECT_STATUS_v02.md](../../PROJECT_STATUS_v02.md) - detailed status

### When Writing Code
1. **Follow**: [local-architecture.mdc](local-architecture.mdc) - module structure
2. **Check**: [local-aptly.mdc](local-aptly.mdc) - aptly patterns
3. **Avoid**: [local-pitfalls.mdc](local-pitfalls.mdc) - common mistakes
4. **Use**: [shared-code-quality.mdc](shared-code-quality.mdc) - quality standards

### Before Commit
Check [local-git-workflow.mdc](local-git-workflow.mdc) and run:
```bash
make format      # Black formatting
make lint        # flake8
make type-check  # mypy
make test        # pytest (263 tests, 30s timeout!)
make check-all   # All checks (coverage 92.98%!)
```

**DON'T commit** if `make check-all` fails!

## 📚 Documentation

All documentation in `docs/`:
- **docs/README.md** - navigation
- **docs/IMPLEMENTATION_PLAN.md** - full implementation plan
- **docs/QUICKSTART.md** - 5-minute quick start
- **docs/CONFIG.md** - configuration reference (v0.2)
- **docs/MIGRATION_v0.2.md** - migration guide
- **docs/ARCHITECTURE.md** - architecture details
- **PROJECT_STATUS_v02.md** - current status
- **COVERAGE_PROGRESS.md** - coverage details

## 🏁 Current Status (v0.2.0)

**Version**: v0.2.0 🚀 (Released 2025-11-07)  
**Package**: https://pypi.org/project/debrepomanager/  
**Coverage**: 92.98% (4 modules at 100%)  
**Tests**: 263 passed  
**Status**: Production Ready ✅

**Recent Changes**:
- v0.2.0: Config refactoring (auto-detection, ENV vars, metadata)
- v0.1.3: Generic URLs
- v0.1.2: English translation
- v0.1.1: Renamed to debrepomanager
- v0.1.0: MVP complete

**Next**: Phases 7-9 (GitHub Actions, Retention, GPG Rotation)

## 🎓 Project Principles

1. **Code Quality First**: 92.98% coverage, all checks passing
2. **Test Everything**: 263 tests with timeouts, fuzzing included
3. **Document Everything**: Comprehensive docs, migration guides
4. **Security Matters**: GPG signing, ENV vars, validation
5. **Aptly Multi-Root**: Isolation per codename
6. **Config Auto-Detection**: Standard tool pattern (git/docker/npm)
7. **Metadata Tracking**: Fast operations, sync recovery
8. **Atomic Updates**: Snapshots for zero-downtime

## 📞 See Also

- **Issues**: https://github.com/jethome-iot/repomanager/issues
- **Docs**: docs/README.md
- **Help**: `make help`
- **Quick Ref**: [local-quick-reference.mdc](local-quick-reference.mdc)
