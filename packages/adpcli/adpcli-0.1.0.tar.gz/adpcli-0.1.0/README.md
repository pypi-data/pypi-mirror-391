# ADP Engine (Provisioning)

Python artifact provisioning engine that reads a YAML configuration file and provisions resources across various development platforms.

## Installation

### Using Make (Recommended)

```bash
make install
```

This will install both production and development dependencies.

### Manual Installation

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (optional)
pip install -r requirements-dev.txt
```

## Usage

### Using Make (Recommended)

```bash
# Run with default config (proyecto.yml)
make run

# Run with custom config file
make run CONFIG=my-config.yml
```

### Manual Execution

```bash
python main.py [proyecto.yml]
```

If no file is specified, it will look for `proyecto.yml` in the current directory.

## Development

### Linting

```bash
make lint
```

Runs flake8 to check code quality and style.

### Code Formatting

```bash
make format
```

Formats code using black.

### Clean Cache Files

```bash
make clean
```

Removes Python cache files and build artifacts.

### Run Tests

```bash
make test
```

Runs tests (if available).

### Available Make Targets

Run `make help` to see all available targets.

## Project Structure

- `orchestrator.py`: Main orchestrator that reads the YAML and coordinates calls
- `github_client.py`: Client for interacting with the GitHub REST API
- `main.py`: CLI entry point
- `requirements.txt`: Production dependencies
- `requirements-dev.txt`: Development dependencies (linter, formatter, etc.)
- `Makefile`: Convenient commands for common tasks
- `.flake8`: Flake8 linter configuration
- `pyproject.toml`: Black formatter and pytest configuration

## Configuration

The `proyecto.yml` file must follow the structure specified in the project documentation.

## Notes

- GitHub token is temporarily hardcoded in `orchestrator.py`
- Organization name must be specified in each call (for now)

