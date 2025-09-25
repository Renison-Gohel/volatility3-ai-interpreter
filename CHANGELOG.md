# Changelog

All notable changes to the AI Interpreter plugin for Volatility 3 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-04-05

### Added
- Support for OpenAI backend with proper error handling
- Support for Ollama backend for local AI processing
- Command validation to reduce AI hallucination
- Comprehensive installation script
- Detailed README with usage examples
- Requirements file for dependency management
- Test script for installation verification
- Security considerations documentation

### Changed
- Improved error handling and user feedback
- Enhanced plugin structure following Volatility 3 best practices
- Better memory file path detection
- More robust AI response parsing

### Fixed
- Syntax errors in plugin code
- Memory file path detection issues
- Command execution reliability
- Dependency installation process

## [1.1.0] - 2025-04-01

### Added
- Initial release of AI Interpreter plugin
- Basic natural language to Volatility command translation
- Simple command execution functionality
- Support for basic Volatility 3 commands

### Changed
- Initial plugin structure and framework integration

## [1.0.0] - 2025-03-28

### Added
- Project inception and initial development
- Core concept implementation
- Basic plugin framework

---

## Versioning Scheme

- MAJOR version when you make incompatible API changes
- MINOR version when you add functionality in a backwards compatible manner
- PATCH version when you make backwards compatible bug fixes

## Release Process

1. Update CHANGELOG.md with changes for the new release
2. Update version numbers in:
   - Plugin file (`_version` variable)
   - CHANGELOG.md (new version entry)
3. Create a git tag for the release
4. Push changes and tag to GitHub
5. Create a GitHub release with release notes