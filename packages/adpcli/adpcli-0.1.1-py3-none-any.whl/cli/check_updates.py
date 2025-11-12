import sys
import os
import subprocess
import requests
import warnings
import logging
from packaging.version import Version
from importlib.metadata import version, PackageNotFoundError

# --- CONFIGURACIÓN DE ACTUALIZACIÓN ---
TOOL_NAME = "adp-cli"  # Debe coincidir con [project].name en pyproject.toml
VERSION_CHECK_URL = "https://backend-adp-admin-production-xwtfd.ecwl-prod.itti-platform.digital/v1/lastversion"
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

    # 2. Obtener la versión mandatoria desde la URL (OBLIGATORIO)
    try:
        # Ignorar advertencias de SSL si usas certificados internos
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = requests.get(VERSION_CHECK_URL, verify=False, timeout=5)
            
        response.raise_for_status() # Lanza error si la URL falla
        
        latest_version_str = response.json()["mandatory_version"]
        latest_version = Version(latest_version_str)

        # Si no hay versión actual instalada, solo verificamos que se pudo conectar
        if current_version is None:
            print(f"Versión mandatoria del servidor: {latest_version_str}")
            print("El paquete no está instalado, pero la verificación de versión fue exitosa.")
            return

        # 3. Comparar versiones
        if current_version == latest_version:
            print("No hay actualizaciones disponibles.")
            return

        if current_version < latest_version:
            print(f"Actualización mandatoria detectada. Tienes {current_version}, se requiere {latest_version}.")
            print("Actualizando automáticamente...")
            
            # 4. Ejecutar la actualización con pip
            # sys.executable asegura que usamos el 'python' correcto
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--upgrade", TOOL_NAME
            ])
            
            print(f"¡Actualización a {latest_version} completada! Reiniciando CLI...")
            
            # 5. Reiniciar el script para usar la nueva versión
            # os.execv reemplaza el proceso actual con el nuevo
            os.execv(sys.executable, [sys.executable] + sys.argv)
            
    except requests.exceptions.Timeout:
        print("Error: No se pudo conectar al servidor de versiones (timeout).", file=sys.stderr)
        print("Verifique la conexión a la vpn Wrap by Cloudflare.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"Error: No se pudo conectar al servidor de versiones: {e}", file=sys.stderr)
        print("La verificación de versión es obligatoria. El programa no puede continuar.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: No se pudo obtener la versión mandatoria del servidor: {e}", file=sys.stderr)
        print("La verificación de versión es obligatoria. El programa no puede continuar.", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Respuesta del servidor no contiene el campo esperado: {e}", file=sys.stderr)
        print("La verificación de versión es obligatoria. El programa no puede continuar.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Ocurrió un error al verificar la actualización: {e}", file=sys.stderr)
        print("La verificación de versión es obligatoria. El programa no puede continuar.", file=sys.stderr)
        sys.exit(1)
