# jps-release-management-utils

Developer utilities for automating software release processes — changelog generation, version bumping, tagging, and artifact publishing.

## 🚀 Overview

This repository serves as the canonical toolkit for release automation. It contains the shared scripts and Makefile patterns used across other projects.

### Features

- Standardized changelog management
- Version bumping utilities
- Automated release workflows
- Pre-commit integration

### Example Usage

```bash
python3 scripts/release_project.py --minor
```

## 📦 Installation

```bash
pip install -e .[dev]
```

## 🧪 Development

```bash
make lint
make test
```

## 📜 License

MIT License © Jaideep Sundaram
