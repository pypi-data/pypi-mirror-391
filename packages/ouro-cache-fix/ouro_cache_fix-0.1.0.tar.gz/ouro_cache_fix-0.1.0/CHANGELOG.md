# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Type checking support with `py.typed` marker
- Comprehensive logging for debugging (DEBUG level)
- Memory management with `max_cache_size` parameter and `clear()` method
- Enhanced error messages with debugging context
- Code quality checks (black, flake8, mypy) in CI/CD
- PyPI auto-publishing workflow on releases
- Python 3.12 support in CI matrix

### Changed

- Improved error messages with actionable debugging hints
- Single source of truth for version (reads from `pyproject.toml`)
- Removed `setup.py` in favor of modern `pyproject.toml` only

### Fixed

- Type hints coverage now 100% with mypy validation

## [0.1.0] - 2024-11-08

### Added

- Initial release of `UniversalTransformerCache`
- Support for Ouro-1.4B Universal Transformer architecture (4 UT steps)
- Fixes `IndexError: list index out of range` when using `use_cache=True`
- Comprehensive test suite with 24 test cases
  - Basic cache operations
  - Error handling validation
  - Beam search support
  - Memory management
- CI/CD workflows for automated testing
  - Multi-Python version testing (3.8-3.12)
  - Multi-OS testing (Ubuntu, macOS)
  - Code coverage reporting to codecov
- Full documentation and usage examples
- Example script demonstrating basic usage
- MIT License

### Performance

- 1.9x faster than `use_cache=False`
- Preserves all 4 Universal Transformer loops
- Compatible with base and fine-tuned models

[Unreleased]: https://github.com/Antizana/ouro-cache-fix/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Antizana/ouro-cache-fix/releases/tag/v0.1.0
