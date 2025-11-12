# Development Guide

## Local Installation for Development

This guide explains how to install `sifi-bridge-py` locally for development using **uv**, a fast Python package manager.

### Prerequisites

Install uv if you don't have it:

```bash
# Using pipx (recommended)
pipx install uv

# Or using pip
pip install --user uv

# Or using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Version Management

The package version is managed in `pyproject.toml` under `[project]` → `version`.

To update the version:
1. Edit `pyproject.toml`
2. Change the `version` field (e.g., `"2.0.0-beta.1"` → `"2.0.0-beta.2"`)
3. Run `uv sync` to reinstall with the new version

**Note on version formats:** Python follows PEP 440 which normalizes version strings. For example:
- `"2.0.0-beta.1"` → displayed as `2.0.0b1`
- `"2.0.0-alpha.1"` → displayed as `2.0.0a1`
- `"2.0.0-rc.1"` → displayed as `2.0.0rc1`

This is expected behavior and both formats are equivalent.

### Quick Start

The simplest way to get started:

```bash
# Install all dependencies and the package in editable mode
uv sync

# The package is now installed! Run Python via uv:
uv run python your_script.py

# Or run a specific command
uv run pytest tests/
```

That's it! `uv sync` automatically:

- Creates a virtual environment (`.venv/`)
- Installs all dependencies from `pyproject.toml`
- Installs your package in editable mode
- Generates/updates `uv.lock`

### Installation Options

#### Install with Extra Dependencies

```bash
# Install with main dependencies only
uv sync

# Install with optional dependencies (e.g., examples)
uv sync --extra examples

# Install all optional dependencies
uv sync --all-extras
```

#### Running Commands

```bash
# Run Python scripts
uv run python examples/example.py

# Run tests
uv run pytest tests/

# Run any command in the uv environment
uv run <command>
```

#### Activate the Virtual Environment (Optional)

If you prefer to activate the virtual environment manually:

```bash
# Activate the environment
source .venv/bin/activate

# Now you can use python/pip directly
python your_script.py
pytest tests/
```

### Development Workflow

1. **Make changes** to the source code in `sifi_bridge_py/`
2. **Test your changes** - they're immediately available (editable install)
   ```bash
   uv run python -c "import sifi_bridge_py; print(sifi_bridge_py.__file__)"
   ```
3. **Update version** when ready to release:
   - Edit the `version` field in `pyproject.toml`
   - Run `uv sync` to update the lock file
   - Commit the changes
4. **Build the package**:
   ```bash
   uv build
   ```
   This creates distribution files in `dist/`

### Publishing to PyPI

```bash
# Build the package
uv build

# Publish to PyPI (requires PyPI credentials)
uv publish

# Or publish to TestPyPI first
uv publish --publish-url https://test.pypi.org/legacy/
```

You can also use `twine` if you prefer:

```bash
uv build
uv run twine upload dist/*
```

### Adding Dependencies

```bash
# Add a runtime dependency
uv add requests

# Add a development dependency
uv add --dev pytest

# Add an optional dependency (to a group)
uv add --optional examples matplotlib
```

This automatically updates `pyproject.toml` and `uv.lock`.

### Other Useful Commands

```bash
# Update all dependencies
uv sync --upgrade

# Remove a dependency
uv remove package-name

# Show installed packages
uv pip list

# Lock dependencies without installing
uv lock

# Clean the virtual environment
rm -rf .venv
uv sync  # Recreate
```

### Verifying the Installation

After running `uv sync`, verify it works:

```bash
uv run python -c "import sifi_bridge_py; print(f'Package: {sifi_bridge_py.__name__}'); print(f'Location: {sifi_bridge_py.__file__}')"
```

You should see the package name and path pointing to your local development directory.

### Migration Notes

This project has been migrated from PDM to uv. Key changes:
- Build backend changed from `pdm-backend` to `hatchling`
- Lock file changed from `pdm.lock` to `uv.lock`
- Development workflow now uses `uv` commands instead of `pdm`

### Notes

- Changes to source code are immediately reflected (no reinstall needed)
- The `.venv/` directory is created automatically by uv
- The `uv.lock` file should be committed to version control
- uv is significantly faster than traditional pip/poetry/pdm workflows
- For Arch Linux users: uv manages its own virtual environments, so no system Python conflicts
