"""ADP CLI - Artifact Provisioning Engine."""

from pathlib import Path

# Obtener la versión desde pyproject.toml (single source of truth)
def _get_version_from_pyproject():
    """Lee la versión desde pyproject.toml."""
    try:
        import tomllib
        # __init__.py está en src/cli/__init__.py
        # pyproject.toml está en la raíz del proyecto
        # Desde src/cli/__init__.py -> src/cli -> src -> raíz
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data["project"]["version"]
    except Exception as e:
        # Fallback si no se puede leer pyproject.toml
        return "0.0.0"

__version__ = _get_version_from_pyproject()

