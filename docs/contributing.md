# Contributing to SolNet

Thank you for your interest in contributing to SolNet! This project is part of the Esslinger & Co. vision for decentralized, self-improving infrastructure. We welcome contributions from mesh networking enthusiasts, AI/agent developers, privacy technologists, hardware hackers, and documentation writers.

## Code of Conduct

Be respectful, collaborative, and focused on building robust, privacy-respecting technology. We follow standard open-source norms (see Contributor Covenant or similar).

## How to Contribute

1. **Fork** the repository and create a feature branch from `main`.
2. **Implement** your changes with clear commit messages.
3. **Test** thoroughly (unit tests, integration where possible).
4. **Document** new functionality or changes.
5. **Open a Pull Request** against `main` with a clear description of the problem and solution.

## Development Setup

```bash
git clone https://github.com/digitaldesignerjazz/solnet.git
cd solnet
pip install -e ".[dev]"
# Run tests
pytest
# Format
black src tests
# Type check
mypy src
```

## Focus Areas (High Priority)

- **Mesh & Yggdrasil Integration**: Improving peer management, event handling, route optimization.
- **Hyperspace Protocol**: Design discussions and implementation of tunnel management, multiplexing, capability negotiation.
- **AI / Swarm Layer**: Nexus-compatible coordination, emotional models, collective intelligence primitives.
- **Privacy Enhancements**: Additional anonymity layers, traffic analysis resistance, crypto agility.
- **Hardware Integration**: Drivers/adapters for Grok Launcher, Soilnova sensors, Vista Nova interfaces.
- **Documentation & Examples**: Architecture deep-dives, tutorials, runnable demos.
- **Testing & CI**: Expanding test suite, property-based testing, chaos engineering for distributed scenarios.

## Commit & Code Style

- Follow PEP 8 / Black formatting for Python.
- Use type hints everywhere (mypy strict mode target).
- Write clear docstrings (Google or NumPy style).
- For Rust components (future): follow standard Rust idioms and clippy.
- Keep security-sensitive code well-commented and auditable.

## Reporting Issues

Use GitHub Issues. Please include:
- Clear reproduction steps or problem description
- Expected vs actual behavior
- Relevant logs, Yggdrasil version, Python version, OS
- For security issues: follow responsible disclosure (email or private issue if sensitive)

## License

By contributing, you agree that your contributions will be licensed under the MIT License (same as the project).

---

*Together we are building the connective tissue for autonomous, decentralized intelligence.*
