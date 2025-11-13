import sys
import os
import subprocess
import shutil
import requests
from packaging.version import Version
from importlib.metadata import version, PackageNotFoundError

# --- CONFIGURACIÓN DE ACTUALIZACIÓN ---
TOOL_NAME = "adpcli"  # Debe coincidir con [project].name en pyproject.toml
GIT_REPO_URL = "git+ssh://git@github.com/ittidigital/adp-cli"
#LAST_VERSION_API_URL = "https://backend-adp-admin-production-xwtfd.ecwl-prod.itti-platform.digital/v1/lastversion"
LAST_VERSION_API_URL = "http://localhost:8080/v1/lastversion"
# --------------------------------------


def get_current_version():
    """
    Obtiene la versión actual instalada del paquete.
    
    Returns:
        Version: Objeto Version con la versión actual, o None si no está instalado
    """
    try:
        current_version_str = version(TOOL_NAME)
        return Version(current_version_str)
    except PackageNotFoundError:
        return None


def get_mandatory_version():
    """
    Obtiene la versión mandatoria desde el backend.
    Esta es la única fuente de verdad para la versión mandatoria.
    
    Returns:
        Version: Objeto Version con la versión mandatoria
        
    Raises:
        SystemExit: Si no se puede conectar al backend o hay un error
    """
    try:
        response = requests.get(LAST_VERSION_API_URL, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        # El endpoint devuelve: {"mandatory_version":"0.0.1","date":20251107101759}
        if isinstance(data, dict):
            version_str = data.get("mandatory_version")
            if version_str:
                # Log para verificar el valor obtenido
                print(f"INFO: Versión mandatoria obtenida del servicio: {version_str}", file=sys.stderr)
            else:
                # Intentar otros campos como fallback (por compatibilidad)
                version_str = data.get("version") or data.get("lastversion") or data.get("last_version")
        else:
            version_str = str(data)
        
        if not version_str:
            print("ERROR: La API no devolvió una versión válida.", file=sys.stderr)
            print(f"DEBUG: Respuesta recibida: {data}", file=sys.stderr)
            sys.exit(1)
        
        return Version(version_str)
    except requests.exceptions.Timeout:
        print("ERROR: No se pudo conectar con el servicio (timeout).", file=sys.stderr)
        print("La aplicación no puede continuar y se cerrará.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: No se pudo conectar con el servicio: {e}", file=sys.stderr)
        print("La aplicación no puede continuar y se cerrará.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: Error HTTP al obtener la versión mandatoria: {e}", file=sys.stderr)
        print(f"Status code: {e.response.status_code}", file=sys.stderr)
        print("La aplicación no puede continuar y se cerrará.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: Versión mandatoria inválida recibida: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Error inesperado al obtener la versión mandatoria: {e}", file=sys.stderr)
        sys.exit(1)


def install_from_git(version_str=None):
    """
    Instala o actualiza el paquete desde el repositorio Git.
    
    Args:
        version_str: Versión específica a instalar (tag, branch, commit). Si es None, instala la última versión.
    """
    if version_str:
        install_url = f"{GIT_REPO_URL}@{version_str}"
    else:
        install_url = GIT_REPO_URL
    
    print(f"Instalando desde: {install_url}")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "--upgrade", install_url
    ])


def restart_cli():
    """
    Reinicia el CLI usando el comando instalado.
    """
    command_name = "adp-cli"
    command_path = shutil.which(command_name)
    
    if command_path:
        os.execv(command_path, [command_path] + sys.argv[1:])
    else:
        # Fallback: usar python -m cli.main si el comando no se encuentra
        os.execv(sys.executable, [
            sys.executable, "-m", "cli.main"
        ] + sys.argv[1:])


def check_for_updates():
    """
    Verifica la versión mandatoria y se auto-actualiza si es necesario.
    Si no se puede conectar al servidor, el programa termina con error.
    """
    # 1. Obtener la versión actual instalada
    current_version = get_current_version()
    
    # 2. Obtener la versión mandatoria desde el backend (única fuente de verdad)
    mandatory_version = get_mandatory_version()
    
    # 3. Si no hay versión actual instalada, instalar la versión mandatoria
    if current_version is None:
        print(f"Versión mandatoria: {mandatory_version}")
        print("El paquete no está instalado. Instalando versión mandatoria...")
        install_from_git(str(mandatory_version))
        print(f"¡Instalación completada! Reiniciando CLI...")
        restart_cli()
        return
    
    # 4. Comparar versiones
    if current_version == mandatory_version:
        # Ya está en la versión mandatoria, continuar normalmente
        return
    
    if current_version < mandatory_version:
        print(f"Actualización mandatoria disponible.")
        print(f"Versión actual: {current_version}")
        print(f"Versión mandatoria: {mandatory_version}")
        print("Actualizando automáticamente...")
        
        install_from_git(str(mandatory_version))
        
        print(f"¡Actualización a {mandatory_version} completada! Reiniciando CLI...")
        restart_cli()
        return
    
    # Si current_version > mandatory_version, continuar normalmente
    # (puede ser una versión de desarrollo o una versión más nueva)


def upgrade_to_latest():
    """
    Instala la última versión disponible desde el repositorio Git.
    Este comando se ejecuta cuando el usuario usa --upgrade.
    """
    print("Instalando la última versión disponible desde el repositorio...")
    install_from_git()  # Sin versión específica, instala la última
    print("¡Actualización completada! Reiniciando CLI...")
    restart_cli()
