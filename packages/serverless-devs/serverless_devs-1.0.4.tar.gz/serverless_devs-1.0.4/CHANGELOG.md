# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2025-11-11

### Added
- Fully automatic installation on pip install
- Smart s command wrapper with intelligent lookup
- Cross-platform support (Windows/Linux/macOS)
- Non-interactive mode for CI/CD
- Wrapper script ensures s command availability

### Changed
- Improved error messages and troubleshooting guides
- Better Windows encoding compatibility

### Fixed
- Windows Unicode encoding errors
- CI test reliability
- PATH configuration issues


## [1.0.3] - 2025-11-11

### Added
- Bilingual documentation (English + Chinese)
- Real Serverless Devs installation test in CI
- Better badge URLs in README

### Changed
- CI now tests on Python 3.10, 3.11, 3.12
- Package still supports Python 3.7+
- Improved installation error messages

### Fixed
- Fixed README badge display issues
- Fixed CI test for s command

## [1.0.2] - 2025-11-11

### Added
- GitHub Actions auto-publish to PyPI
- Auto-install latest Serverless Devs (no hardcoded version)
- Domestic mirror acceleration support

### Changed
- Changed from binary download to official script installation
- Improved error messages and help information

## [1.0.1] - 2025-11-11

### Fixed
- Fixed Windows installation issues

## [1.0.0] - 2025-11-11

### Added
- Initial release
- Support for Windows, Linux, macOS
- Install Serverless Devs via pip
