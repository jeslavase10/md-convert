# Contributing

Welcome! Thanks for your interest in contributing to md-convert.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/tuuser/md-convert.git
cd md-convert
```

2. Install in development mode:
```bash
pip install -e ".[dev]"
```

3. Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=md_converter

# Run specific test file
pytest tests/test_parser.py

# Run with verbose output
pytest -v
```

## Code Style

We use:
- `black` for code formatting
- `ruff` for linting
- `mypy` for type checking

```bash
# Format code
black md_converter/

# Lint
ruff check md_converter/

# Type check
mypy md_converter/
```

## Project Structure

```
md-convert/
├── src/md_converter/     # Main source code
│   ├── cli.py           # CLI entry point
│   ├── parsers/         # Markdown and diagram parsers
│   ├── renderers/       # PDF and DOCX renderers
│   ├── styles/          # CSS and HTML templates
│   └── utils/           # Utilities
├── tests/               # Test suite
│   ├── fixtures/        # Test fixture files
│   └── test_*.py        # Test modules
├── docs/                # Documentation
└── scripts/             # Build and release scripts
```

## Adding Tests

When adding features:

1. Add tests in appropriate `test_*.py` file
2. Add fixture files in `tests/fixtures/`
3. Update CHANGELOG.md
4. Update docs if needed

## Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Add tests
5. Run the test suite
6. Commit with clear message
7. Push and open a PR

## Bug Reports

Please report bugs with:
- Your environment (OS, Python version)
- md-convert version
- Steps to reproduce
- Expected vs actual behavior
- Error messages if any

## Feature Requests

Open an issue with:
- Description of the feature
- Use case / motivation
- Any alternatives you've considered

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
