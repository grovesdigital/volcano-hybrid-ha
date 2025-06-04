# Contributing to Volcano Hybrid Home Assistant Integration

Thank you for your interest in contributing to the Volcano Hybrid Home Assistant Integration! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Home Assistant 2023.1 or higher
- Git
- A Storz & Bickel Volcano Hybrid device for testing

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/grovesdigital/volcano-hybrid-ha.git
   cd volcano-hybrid-ha
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements_dev.txt
   ```

5. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Guidelines

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) Python style guidelines
- Use type hints for all function parameters and return values
- Add docstrings to all public functions and classes
- Use meaningful variable and function names
- Keep functions focused on a single responsibility

### Code Formatting

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Run these tools before committing:

```bash
black .
isort .
flake8 .
mypy .
```

### Testing

#### Unit Tests

Write unit tests for new functionality:

```bash
pytest tests/
```

#### Integration Tests

Test with a real Home Assistant instance:

1. Copy the integration to your HA `custom_components` directory
2. Add the integration through the UI
3. Test all functionality manually

### Commit Guidelines

- Use clear, descriptive commit messages
- Start with a verb in the imperative mood (e.g., "Add", "Fix", "Update")
- Keep the first line under 50 characters
- Add a detailed description if necessary

Example:
```
Add fan timer functionality

- Implement fan timer service with duration control
- Add timer state tracking in coordinator
- Update fan entity to show timer status
- Add timer controls to Home Assistant UI
```

### Branch Strategy

- Create feature branches from `main`
- Use descriptive branch names: `feature/fan-timer`, `fix/temperature-reading`
- Keep branches focused on a single feature or fix
- Rebase before merging to keep history clean

## Types of Contributions

### Bug Reports

When reporting bugs, please include:

- Home Assistant version
- Integration version
- Device model and firmware version
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs

### Feature Requests

For new features:

- Describe the use case
- Explain the expected behavior
- Consider backward compatibility
- Provide examples if possible

### Code Contributions

#### New Features

1. Create an issue to discuss the feature first
2. Fork the repository and create a feature branch
3. Implement the feature with tests
4. Update documentation
5. Submit a pull request

#### Bug Fixes

1. Create an issue describing the bug (if one doesn't exist)
2. Fork the repository and create a fix branch
3. Implement the fix with tests
4. Submit a pull request

## Pull Request Process

1. **Fork and Branch**: Create a feature branch from `main`
2. **Develop**: Make your changes following the guidelines above
3. **Test**: Ensure all tests pass and add new tests for your changes
4. **Document**: Update relevant documentation
5. **Commit**: Make clean, logical commits with good messages
6. **Push**: Push your branch to your fork
7. **PR**: Create a pull request with a clear description

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tested with real device
- [ ] All existing tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
```

## Architecture Overview

### Core Components

- **`__init__.py`**: Integration setup and coordinator
- **`config_flow.py`**: Configuration UI and device discovery
- **`const.py`**: Constants and configuration
- **`volcano/api.py`**: Bluetooth communication layer

### Platform Components

- **`climate.py`**: Temperature control
- **`fan.py`**: Fan control and timer
- **`sensor.py`**: Status and statistics sensors
- **`switch.py`**: Binary controls
- **`button.py`**: Action buttons
- **`number.py`**: Numeric controls

### Adding New Platforms

1. Create the platform file (e.g., `light.py`)
2. Add platform to `PLATFORMS` in `const.py`
3. Implement the platform class inheriting from appropriate base
4. Add platform-specific services if needed
5. Update tests and documentation

## Communication Protocol

The integration communicates with the Volcano Hybrid via Bluetooth LE:

- **Service UUID**: `10100000-5354-4f52-5a26-4249434b454c`
- **Commands**: Sent as structured byte arrays
- **Responses**: Parsed from device notifications

### Adding New Commands

1. Define command constants in `const.py`
2. Implement command in `volcano/api.py`
3. Add error handling and validation
4. Update coordinator to use new command
5. Add tests for the new functionality

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Document parameters, return values, and exceptions
- Include usage examples for complex functions

### User Documentation

- Update README.md for user-facing changes
- Add configuration examples
- Update troubleshooting section if needed
- Document any breaking changes

## Release Process

1. Update version in `manifest.json`
2. Update `CHANGELOG.md` with new features and fixes
3. Create a release branch
4. Test thoroughly
5. Create GitHub release with detailed notes
6. Update HACS repository (if applicable)

## Community

### Communication

- Use GitHub issues for bug reports and feature requests
- Join Home Assistant Discord for general discussion
- Be respectful and constructive in all interactions

### Code of Conduct

- Be welcoming to newcomers
- Respect different viewpoints and experiences
- Focus on what's best for the community
- Show empathy towards other community members

## Questions?

If you have questions about contributing:

1. Check existing issues and documentation
2. Create a new issue with the "question" label
3. Join the Home Assistant community forums

Thank you for contributing to the Volcano Hybrid Home Assistant Integration!
