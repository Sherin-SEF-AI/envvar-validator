# Contributing to env-validator

Thank you for your interest in contributing to env-validator! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A code editor (VS Code, PyCharm, etc.)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/env-validator.git
   cd env-validator
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Run tests to ensure everything works**
   ```bash
   pytest
   ```

## 🛠️ Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Run these tools before committing:

```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

### Testing

We use pytest for testing. Write tests for all new features and bug fixes.

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/env_validator

# Run specific test file
pytest tests/test_validator.py

# Run tests with verbose output
pytest -v
```

### Documentation

- Update docstrings for all new functions and classes
- Follow Google-style docstring format
- Update README.md if adding new features
- Update API documentation if changing public interfaces

## 📝 Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   pre-commit run --all-files
   pytest
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new validator for X"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks

Examples:
```
feat: add new email validator
fix: resolve issue with boolean parsing
docs: update README with new examples
```

## 🧪 Adding New Validators

To add a new validator:

1. **Create the validator class**
   ```python
   from .base import BaseValidator, ValidationError, ValidationContext, validator
   
   @validator("your_validator_name")
   class YourValidator(BaseValidator):
       def __init__(self, **kwargs):
           super().__init__(**kwargs)
           self.examples = ["example1", "example2"]
           self.suggestions = ["suggestion1", "suggestion2"]
       
       def validate(self, value: Any, context: Optional[ValidationContext] = None) -> Any:
           # Your validation logic here
           return value
   ```

2. **Add tests**
   ```python
   def test_your_validator():
       validator = YourValidator()
       # Test valid cases
       assert validator.validate("valid_value") == "valid_value"
       
       # Test invalid cases
       with pytest.raises(ValidationError):
           validator.validate("invalid_value")
   ```

3. **Update documentation**
   - Add to the validators list in README.md
   - Update API documentation

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Environment information**
   - Python version
   - Operating system
   - env-validator version

2. **Steps to reproduce**
   - Clear, step-by-step instructions
   - Minimal code example

3. **Expected vs actual behavior**
   - What you expected to happen
   - What actually happened

4. **Additional context**
   - Error messages
   - Stack traces
   - Screenshots (if applicable)

## 💡 Feature Requests

When requesting features:

1. **Describe the problem**
   - What problem are you trying to solve?
   - Why is this feature needed?

2. **Propose a solution**
   - How should this feature work?
   - Any specific requirements or constraints?

3. **Provide examples**
   - Code examples of how you'd use the feature
   - Expected behavior

## 📋 Issue Templates

We have issue templates for:
- Bug reports
- Feature requests
- Documentation improvements
- Security vulnerabilities

Please use the appropriate template when creating issues.

## 🤝 Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) for details.

## 📞 Getting Help

If you need help:

1. **Check existing issues** - Your question might already be answered
2. **Search documentation** - Check README.md and docstrings
3. **Create an issue** - Use the appropriate template
4. **Join discussions** - Use GitHub Discussions for general questions

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

## 📄 License

By contributing to env-validator, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to env-validator! 🎉 