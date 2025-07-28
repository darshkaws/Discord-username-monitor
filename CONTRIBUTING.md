## CONTRIBUTING.md

# Contributing to Discord Username Monitor

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and professional
- Focus on constructive feedback
- Help maintain a welcoming environment
- Report any inappropriate behavior

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a virtual environment
4. Install development dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use Black for code formatting
- Run flake8 for linting
- Add type hints where appropriate

```bash
black src/
flake8 src/
mypy src/
```

### Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for good test coverage

```bash
pytest tests/
```

### Documentation

- Update docstrings for new functions
- Update README.md if needed
- Add examples for new features

## Submitting Changes

1. Create a feature branch from main
2. Make your changes with clear commits
3. Test your changes thoroughly
4. Update documentation as needed
5. Submit a pull request

### Pull Request Guidelines

- Provide clear description of changes
- Reference any related issues
- Include test results
- Keep changes focused and atomic

## Areas for Contribution

### High Priority
- Improved error handling
- Performance optimizations
- Better proxy support
- Enhanced logging

### Medium Priority
- Additional username sources
- UI improvements
- Configuration management
- Documentation improvements

### Feature Requests
- New notification methods
- Advanced filtering options
- Statistics and analytics
- Multi-platform support

## Security Considerations

- Never commit tokens or credentials
- Be careful with user data handling
- Follow responsible disclosure for vulnerabilities
- Consider rate limiting implications

## Questions?

- Open an issue for questions
- Join discussions in GitHub Discussions
- Check existing issues before reporting bugs

Thank you for contributing!

