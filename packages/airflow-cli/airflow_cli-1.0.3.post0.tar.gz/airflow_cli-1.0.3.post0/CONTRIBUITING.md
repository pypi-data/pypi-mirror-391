# 🤝 Contributing to Airflow CLI

First off, thank you for considering contributing to Airflow CLI! It's people like you that make this tool better for everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to ufpblema@gmail.com.

## Getting Started

### Types of Contributions

We love contributions! Here are some ways you can help:

- 🐛 **Bug Reports**: Found a bug? Let us know!
- ✨ **Feature Requests**: Have an idea? We'd love to hear it!
- 📝 **Documentation**: Help improve our docs
- 💻 **Code**: Fix bugs or implement features
- 🧪 **Tests**: Add or improve test coverage
- 🌍 **Translations**: Help translate the CLI

### Before You Start

1. Check existing [issues](https://github.com/lema-ufpb/airflow-cli/issues) and [pull requests](https://github.com/lema-ufpb/airflow-cli/pulls)
2. For major changes, open an issue first to discuss
3. Make sure you have the required tools installed

## Development Setup

### Prerequisites

- Python 3.7+
- Docker & Docker Compose
- Git
- Make (optional, but recommended)

### Setup Steps

1. **Fork the repository**

   Click the "Fork" button on GitHub

2. **Clone your fork**

   ```bash
   git clone https://github.com/YOUR-USERNAME/airflow-cli.git
   cd airflow-cli
   ```

3. **Add upstream remote**

   ```bash
   git remote add upstream https://github.com/lema-ufpb/airflow-cli.git
   ```

4. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install in development mode**

   ```bash
   make install-dev
   # Or manually:
   pip install -e ".[dev]"
   ```

6. **Verify installation**

   ```bash
   actl --help
   ```

## Making Changes

### Branch Naming

Use descriptive branch names:

- `feature/add-new-command` - For new features
- `fix/docker-up-error` - For bug fixes
- `docs/improve-readme` - For documentation
- `test/add-unit-tests` - For tests

### Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### Make Your Changes

1. Write your code
2. Add/update tests
3. Update documentation
4. Run tests locally

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
git commit -m "feat(cli): add restart command for services"
git commit -m "fix(docker): resolve port conflict detection"
git commit -m "docs(readme): add troubleshooting section"
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_cli.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Writing Tests

Place tests in the `tests/` directory:

```python
# tests/test_docker_utils.py
import pytest
from src.docker_utils import docker_up

def test_docker_up():
    """Test docker_up function"""
    # Your test code here
    pass
```

### Testing Your Changes

Before submitting:

```bash
# 1. Run linter
make lint

# 2. Format code
make format

# 3. Run tests
make test

# 4. Test the CLI manually
actl up
actl status
actl down
```

## Code Style

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 120 characters
- **Imports**: Organized with `isort`
- **Formatting**: Use `black`
- **Linting**: Use `flake8`

### Automatic Formatting

```bash
# Format code
make format

# Check formatting
make format-check

# Run linter
make lint
```

### Code Organization

```python
# Standard library imports
import os
import sys

# Third-party imports
import yaml
from pathlib import Path

# Local imports
from .utils import helper_function
```

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.
    
    More detailed explanation if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When something goes wrong
    
    Example:
        >>> example_function("test", 42)
        True
    """
    pass
```

## Submitting Changes

### Pull Request Process

1. **Update your branch**

   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**

   - Go to GitHub and click "New Pull Request"
   - Select your branch
   - Fill out the PR template
   - Link related issues

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] PR description is clear

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
Describe how you tested your changes

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code formatted
```

## Review Process

1. **Automated checks** run on your PR
2. **Maintainer review** - may request changes
3. **Address feedback** - make requested changes
4. **Approval** - once approved, we'll merge!

### After Your PR is Merged

1. Delete your branch
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

2. Update your main branch
   ```bash
   git checkout main
   git pull upstream main
   ```

## Getting Help

Need help? Here's how to reach us:

- 💬 **GitHub Discussions**: Ask questions
- 🐛 **Issues**: Report bugs or suggest features
- 📧 **Email**: ufpblema@gmail.com

## Recognition

Contributors will be:
- Listed in our README
- Mentioned in release notes
- Added to our contributors page

Thank you for contributing! 🎉

---

*This guide is inspired by open-source best practices and adapted for our project.*