import sys
import os
import subprocess
import shutil
import requests
import warnings
import logging
from packaging.version import Version
from importlib.metadata import version, PackageNotFoundError

# --- CONFIGURACIÓN DE ACTUALIZACIÓN ---
TOOL_NAME = "adpcli"  # Debe coincidir con [project].name en pyproject.toml
PYPI_API_URL = f"https://pypi.org/pypi/{TOOL_NAME}/json"
# --------------------------------------

def check_for_updates():
    """
    Verifica la versión mandatoria y se auto-actualiza si es necesario.
    """
    # 1. Obtener la versión actual instalada (si está instalado)
    current_version = None
    try:
        current_version_str = version(TOOL_NAME)
        current_version = Version(current_version_str)
    except PackageNotFoundError:
        # Si no está instalado, continuamos para verificar la versión mandatoria
        pass

    # 2. Obtener la última versión disponible desde PyPI
    try:
        response = requests.get(PYPI_API_URL, timeout=10)
        response.raise_for_status() # Lanza error si la URL falla
        
        pypi_data = response.json()
        # Obtener la última versión de los releases
        releases = pypi_data.get("releases", {})
        if not releases:
            raise ValueError("No se encontraron releases en PyPI")
        
        # Obtener todas las versiones y ordenarlas
        versions = [Version(v) for v in releases.keys() if v]
        latest_version = max(versions)
        latest_version_str = str(latest_version)

        # Si no hay versión actual instalada, solo verificamos que se pudo conectar
        if current_version is None:
            # No mostrar mensaje si no está instalado (evita ruido)
            return

        # 3. Comparar versiones
        if current_version == latest_version:
            # No mostrar mensaje si ya está actualizado (evita ruido)
            return

        if current_version < latest_version:
            print(f"Actualización disponible. Versión actual: {current_version}, última versión: {latest_version}")
            print("Actualizando automáticamente...")
            
            # 4. Ejecutar la actualización con pip
            # sys.executable asegura que usamos el 'python' correcto
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--upgrade", TOOL_NAME
            ])
            
            print(f"¡Actualización a {latest_version} completada! Reiniciando CLI...")
            
            # 5. Reiniciar usando el comando instalado en lugar del script directo
            # Buscar el comando 'adp-cli' en el PATH
            import shutil
            command_name = "adp-cli"
            command_path = shutil.which(command_name)
            
            if command_path:
                # Usar el comando instalado
                os.execv(command_path, [command_path] + sys.argv[1:])
            else:
                # Fallback: usar python -m cli.main si el comando no se encuentra
                os.execv(sys.executable, [
                    sys.executable, "-m", "cli.main"
                ] + sys.argv[1:])
            
    except requests.exceptions.Timeout:
        print("Advertencia: No se pudo conectar a PyPI (timeout). Continuando con la versión actual.", file=sys.stderr)
        # No salir con error, solo continuar con la versión actual
        return
    except requests.exceptions.ConnectionError as e:
        print(f"Advertencia: No se pudo conectar a PyPI: {e}", file=sys.stderr)
        print("Continuando con la versión actual instalada.", file=sys.stderr)
        return
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Advertencia: El paquete '{TOOL_NAME}' no se encontró en PyPI.", file=sys.stderr)
            print("Continuando con la versión actual instalada.", file=sys.stderr)
        else:
            print(f"Advertencia: Error al obtener información de PyPI: {e}", file=sys.stderr)
            print("Continuando con la versión actual instalada.", file=sys.stderr)
        return
    except ValueError as e:
        print(f"Advertencia: {e}", file=sys.stderr)
        print("Continuando con la versión actual instalada.", file=sys.stderr)
        return
    except Exception as e:
        print(f"Advertencia: Ocurrió un error al verificar la actualización: {e}", file=sys.stderr)
        print("Continuando con la versión actual instalada.", file=sys.stderr)
        return
