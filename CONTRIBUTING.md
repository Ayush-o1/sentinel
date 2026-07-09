# Contributing to SENTINEL

First off, thank you for considering contributing to SENTINEL! It's people like you that make SENTINEL such a great tool for the community.

## 1. Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check the [Issues](https://github.com/Ayush-o1/sentinel/issues) tab to see if it's already being tracked. If not, feel free to open a new issue!

## 2. Setting up your environment

SENTINEL is built with a modern stack. You will need:
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

The easiest way to get started is by following the **[Developer Guide](docs/developer-guide.md)** for a full local setup.

## 3. Making Changes

- **Create a branch**: Branch off from `main` (e.g., `feature/awesome-new-feature` or `fix/issue-123`).
- **Code Style**: 
  - **Backend**: We use `ruff` for all Python linting and formatting. Run `ruff check .` and `ruff format .` before committing.
  - **Frontend**: We use `eslint` and `prettier`. Run `npm run lint` and `npm run format`.
- **Tests**: Write tests for any new functionality. Run tests locally via `pytest` (backend) or check the CI pipeline.

## 4. Submitting a Pull Request

1. Push your branch to your fork.
2. Open a Pull Request against the `main` branch.
3. Ensure the CI pipeline passes (tests, linting, build).
4. A maintainer will review your code. We may suggest some changes or improvements.

## 5. Security

If you discover a security vulnerability, please do **NOT** open a public issue. Instead, refer to our [Security Policy](docs/security.md) for instructions on how to responsibly disclose the issue.

Thank you for contributing!
