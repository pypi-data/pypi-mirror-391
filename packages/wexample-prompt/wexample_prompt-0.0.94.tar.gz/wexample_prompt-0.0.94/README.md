# wexample-prompt

Version: 0.0.94

Helper for your tty interactions

## Prompt IO Quickstart

### WithIoManager: owning or sharing the IoManager
- Any class that needs prompt output should inherit `WithIoManager`.
- Call `self.ensure_io_manager()` to lazily create or reuse an `IoManager`.
- To inherit a parent’s indentation/verbosity, call `self.set_parent_io_handler(parent)`; every context you create is automatically nested +1.
- If someone else instantiates the manager, call `self.use_io_manager(io)` to reuse it instead of creating a new instance.

### WithIoMethods: direct method proxies
- Mix in `WithIoMethods` when you want to call `self.log(...)`, `self.separator(...)`, etc., without reaching into `self.io`.
- The mixin delegates missing attribute lookups to the underlying `IoManager`, and it automatically injects `context=self.create_io_context()` so nested logging just works.

### Typical pattern
```python
from wexample_prompt.mixins.with_io_methods import WithIoMethods

class Worker(WithIoMethods):
    def __attrs_post_init__(self):
        self.ensure_io_manager()          # Owns an IoManager

    def run(self):
        self.log("top level message")     # via WithIoMethods

class Child(WithIoMethods):
    def __attrs_post_init__(self, parent):
        self.set_parent_io_handler(parent)  # reuse & indent

    def run(self):
        self.log("nested message")
```

The executor or parent decides whether to create a fresh manager or cascade an existing one; children only call `ensure_io_manager()` and never worry about the init order.

## Tests

This project uses `pytest` for testing and `pytest-cov` for code coverage analysis.

### Installation

First, install the required testing dependencies:
```bash
.venv/bin/python -m pip install pytest pytest-cov
```

### Basic Usage

Run all tests with coverage:
```bash
.venv/bin/python -m pytest --cov --cov-report=html
```

### Common Commands
```bash
# Run tests with coverage for a specific module
.venv/bin/python -m pytest --cov=your_module

# Show which lines are not covered
.venv/bin/python -m pytest --cov=your_module --cov-report=term-missing

# Generate an HTML coverage report
.venv/bin/python -m pytest --cov=your_module --cov-report=html

# Combine terminal and HTML reports
.venv/bin/python -m pytest --cov=your_module --cov-report=term-missing --cov-report=html

# Run specific test file with coverage
.venv/bin/python -m pytest tests/test_file.py --cov=your_module --cov-report=term-missing
```

### Viewing HTML Reports

After generating an HTML report, open `htmlcov/index.html` in your browser to view detailed line-by-line coverage information.

### Coverage Threshold

To enforce a minimum coverage percentage:
```bash
.venv/bin/python -m pytest --cov=your_module --cov-fail-under=80
```

This will cause the test suite to fail if coverage drops below 80%.

## Code Quality & Typing

All the suite packages follow strict quality standards:

- **Type hints**: Full type coverage with mypy validation
- **Code formatting**: Enforced with black and isort
- **Linting**: Comprehensive checks with custom scripts and tools
- **Testing**: High test coverage requirements

These standards ensure reliability and maintainability across the suite.

## Versioning & Compatibility Policy

Wexample packages follow **Semantic Versioning** (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

We maintain backward compatibility within major versions and provide clear migration guides for breaking changes.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and release notes.

Major changes are documented with migration guides when applicable.

## Migration Notes

When upgrading between major versions, refer to the migration guides in the documentation.

Breaking changes are clearly documented with upgrade paths and examples.

## Known Limitations & Roadmap

Current limitations and planned features are tracked in the GitHub issues.

See the [project roadmap](https://github.com/wexample/python-prompt/issues) for upcoming features and improvements.

## Security Policy

### Reporting Vulnerabilities

If you discover a security vulnerability, please email security@wexample.com.

**Do not** open public issues for security vulnerabilities.

We take security seriously and will respond promptly to verified reports.

## Privacy & Telemetry

This package does **not** collect any telemetry or usage data.

Your privacy is respected — no data is transmitted to external services.

## Support Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community support
- **Documentation**: Comprehensive guides and API reference
- **Email**: contact@wexample.com for general inquiries

Community support is available through GitHub Discussions.

## Contribution Guidelines

We welcome contributions to the Wexample suite! 

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

## Maintainers & Authors

Maintained by the Wexample team and community contributors.

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for the full list of contributors.

## License

MIT

## Useful Links

- **Homepage**: https://github.com/wexample/python-prompt
- **Documentation**: [docs.wexample.com](https://docs.wexample.com)
- **Issue Tracker**: https://github.com/wexample/python-prompt/issues
- **Discussions**: https://github.com/wexample/python-prompt/discussions
- **PyPI**: [pypi.org/project/wexample-prompt](https://pypi.org/project/wexample-prompt/)

## Integration in the Suite

This package is part of the **Wexample Suite** — a collection of high-quality Python packages designed to work seamlessly together.

### Related Packages

The suite includes packages for configuration management, file handling, prompts, and more. Each package can be used independently or as part of the integrated suite.

Visit the [Wexample Suite documentation](https://docs.wexample.com) for the complete package ecosystem.

# About us

Wexample stands as a cornerstone of the digital ecosystem — a collective of seasoned engineers, researchers, and creators driven by a relentless pursuit of technological excellence. More than a media platform, it has grown into a vibrant community where innovation meets craftsmanship, and where every line of code reflects a commitment to clarity, durability, and shared intelligence.

This packages suite embodies this spirit. Trusted by professionals and enthusiasts alike, it delivers a consistent, high-quality foundation for modern development — open, elegant, and battle-tested. Its reputation is built on years of collaboration, refinement, and rigorous attention to detail, making it a natural choice for those who demand both robustness and beauty in their tools.

Wexample cultivates a culture of mastery. Each package, each contribution carries the mark of a community that values precision, ethics, and innovation — a community proud to shape the future of digital craftsmanship.

