# Contributing to py-wallet-pass

Thank you for your interest in contributing to py-wallet-pass! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We're all here to build something great together.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally: `git clone https://github.com/yourusername/py-wallet-pass.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment: 
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
5. Install development dependencies: `pip install -e ".[dev]"` or `poetry install --with dev`
6. Create a branch for your changes: `git checkout -b feature/your-feature-name`

## Development Environment

This project uses Poetry for dependency management. If you have Poetry installed:

```bash
# Install dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Run linter
poetry run ruff check .

# Format code
poetry run black .
```

## Making Changes

1. Make your changes in your feature branch
2. Add or update tests as necessary
3. Run the tests to ensure they pass: `pytest`
4. Format your code: `black .`
5. Lint your code: `ruff check .`
6. Commit your changes with a descriptive commit message
7. Push your changes to your fork on GitHub
8. Submit a pull request to the main repository

## Pull Request Guidelines

- Include a clear description of the changes and their purpose
- Include or update tests for the changes you've made
- Ensure all tests pass and the code is properly formatted
- Link any related issues in the pull request description
- Be ready to address feedback and make changes if requested

## Code Style

This project follows these code style guidelines:

- We use Black for code formatting
- We use Ruff for linting
- We follow PEP 8 conventions
- We use type hints wherever possible
- We write docstrings for all public functions, classes, and methods using Google style
- We keep code modular and DRY (Don't Repeat Yourself)

## Testing

- We use pytest for testing
- All new features should include tests
- Bug fixes should include tests that would have caught the bug
- Run the full test suite before submitting a pull request

## Documentation

- We use Markdown for documentation
- Update the README.md and documentation files as necessary (in ./docs)
- Include examples for new features
- Document any breaking changes

## Releasing??

1. Update version in pyproject.toml
2. Update CHANGELOG.md
3. Create a new GitHub release with release notes
4. GitHub Actions will publish the package to PyPI

## Questions?

If you have any questions about contributing, please open an issue and we'll be happy to help!