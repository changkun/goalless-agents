# Contributing to SmartCommit

Thank you for your interest in contributing to SmartCommit! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/smartcommit.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `python3 test_smartcommit.py`
6. Commit your changes (use SmartCommit itself!)
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

SmartCommit currently has no external dependencies! Just Python 3.6+:

```bash
# Clone the repository
git clone https://github.com/yourusername/smartcommit.git
cd smartcommit

# Make the script executable
chmod +x smartcommit.py

# Run tests
python3 test_smartcommit.py

# Try it out (requires a git repo with staged changes)
./smartcommit.py
```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions focused and single-purpose
- Add tests for new functionality

## Testing

All contributions should include tests:

```bash
# Run all tests
python3 test_smartcommit.py -v

# Run specific test
python3 test_smartcommit.py TestCommitAnalyzer.test_determine_type_feature
```

### Writing Tests

- Place tests in `test_smartcommit.py`
- Use descriptive test names: `test_<what>_<scenario>`
- Test both happy paths and edge cases
- Mock external dependencies (git commands)

## Adding New Features

Before adding a major feature:

1. Open an issue to discuss the feature
2. Get feedback from maintainers
3. Follow the development process above

### Feature Ideas

- Integration with AI APIs (OpenAI, Anthropic)
- Support for custom commit templates
- Git hooks integration
- Configuration file support
- Multi-language support
- Enhanced diff analysis

## Commit Messages

We use Conventional Commits! SmartCommit can help:

```bash
git add .
./smartcommit.py --interactive
```

Format: `<type>(<scope>): <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance tasks

## Pull Request Process

1. Update README.md with details of changes if needed
2. Update EXAMPLES.md with new examples if applicable
3. Add or update tests
4. Ensure all tests pass
5. Update documentation
6. Follow the PR template

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Examples added/updated if needed
- [ ] Commit messages follow conventions
- [ ] No breaking changes (or clearly documented)

## Reporting Bugs

Open an issue with:

- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)
- Sample git diff if relevant

## Code Review

All submissions require review. We aim to:

- Respond to PRs within 48 hours
- Provide constructive feedback
- Maintain high code quality
- Be welcoming to new contributors

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Open an issue with the `question` label or reach out to maintainers.

## Recognition

Contributors will be recognized in:
- README.md (Contributors section)
- Release notes
- GitHub contributors page

Thank you for making SmartCommit better!
