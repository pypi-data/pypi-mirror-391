"""
Main entry point for the ADP Engine.
Executes artifact provisioning based on the configuration file.
"""

import sys
import os
import re
import yaml
import tempfile
import click
from typing import Dict, Any
from importlib.metadata import version, PackageNotFoundError
from .orchestrator import Orchestrator
from .github_client import GitHubClient
from .check_updates import check_for_updates, upgrade_to_latest


def get_version():
    """Get the current version of the package."""
    # Primero intentar obtener la versión del código fuente (modo desarrollo)
    try:
        from . import __version__
        return __version__
    except (ImportError, AttributeError):
        pass
    
    # Si no está disponible, intentar desde el paquete instalado
    try:
        return version("adpcli")
    except PackageNotFoundError:
        # Último recurso: leer desde pyproject.toml
        try:
            import tomllib
            with open("pyproject.toml", "rb") as f:
                data = tomllib.load(f)
                return data["project"]["version"]
        except Exception:
            return "0.0.0"  # Fallback a la versión actual


def validate_environment():
    """
    Valida que todas las variables de entorno necesarias estén configuradas.
    
    Returns:
        tuple: (is_valid, error_message)
        - is_valid: True si todas las validaciones pasan, False en caso contrario
        - error_message: Mensaje de error si alguna validación falla, None si todo está bien
    """
    errors = []
    
    # Validación 1: ADP_GIT_HUB_TOKEN
    github_token = os.getenv("ADP_GIT_HUB_TOKEN")
    if not github_token:
        errors.append("ADP_GIT_HUB_TOKEN: Variable de entorno no configurada")
    elif not github_token.strip():
        errors.append("ADP_GIT_HUB_TOKEN: Variable de entorno está vacía")
    
    if errors:
        error_message = "Errores de validación:\n" + "\n".join(f"  - {error}" for error in errors)
        return False, error_message
    
    return True, None


@click.group(invoke_without_command=True)
@click.version_option(version=get_version(), prog_name="adp")
@click.pass_context
def cli(ctx):
    """Provisioning Engine (ADP Engine) - Provisions artifacts from proyecto.yml"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def validate_repo_name(value: str) -> str:
    """Validate repository name: no spaces, only allowed character is '-'"""
    if not value or not value.strip():
        raise ValueError("Repository name cannot be empty.")
    
    value = value.strip()
    
    pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(pattern, value):
        raise ValueError(
            "Repository name must contain only alphanumeric characters, hyphens, and underscores. No spaces allowed."
        )
    
    if ' ' in value:
        raise ValueError("Repository name cannot contain spaces.")
    
    return value


def collect_github_repository_info() -> Dict[str, Any]:
    """Collect GitHub repository information interactively."""
    click.echo("\n📦 Sección GitHub Repository")
    click.echo("=" * 50)
    
    # Repository Organization
    click.echo("\nPregunta: Repository Organización")
    organizations = ["ittidigital"]
    for idx, org in enumerate(organizations, 1):
        click.echo(f"  {idx}- {org}")
    
    org_choice = click.prompt(
        "\nSelecciona una opción",
        type=click.IntRange(1, len(organizations)),
        default=1
    )
    org_name = organizations[org_choice - 1]
    
    # Repository Name - always required, no default
    click.echo("\nPregunta: Repository Name")
    while True:
        try:
            repo_name = click.prompt("Ingresa el nombre del repositorio", type=str)
            validate_repo_name(repo_name)
            break
        except ValueError as e:
            click.echo(f"❌ Error: {e}", err=True)
            click.echo("Por favor, intenta nuevamente.\n")
    
    # Repository Description
    click.echo("\nPregunta: Repository Description")
    description = click.prompt("Ingresa la descripción del repositorio", type=str, default="")
    
    return {
        "org_name": org_name,
        "repo_name": repo_name,
        "description": description
    }


def collect_workflow_info() -> Dict[str, Any]:
    """Collect workflow information interactively."""
    click.echo("\n🔄 Sección Workflow")
    click.echo("=" * 50)
    
    click.echo("\nPregunta: Workflow")
    workflows = ["Git Flow", "Github Flow", "No por ahora"]
    for idx, workflow in enumerate(workflows, 1):
        click.echo(f"  {idx}- {workflow}")
    
    workflow_choice = click.prompt(
        "\nSelecciona una opción",
        type=click.IntRange(1, len(workflows)),
        default=2
    )
    workflow_name = workflows[workflow_choice - 1]
    
    return {
        "workflow": workflow_name
    }


def collect_user_input() -> Dict[str, Any]:
    """Collect all user input interactively."""
    data = {}
    
    # GitHub Repository Section
    data["github"] = collect_github_repository_info()
    
    # Workflow Section
    data["workflow"] = collect_workflow_info()
    
    # Add more sections here in the future
    # data["sonar"] = collect_sonar_info()
    # data["jenkins"] = collect_jenkins_info()
    
    return data


def display_summary(data: Dict[str, Any]) -> None:
    """Display collected data summary."""
    click.echo("\n" + "=" * 50)
    click.echo("📋 Resumen de configuración")
    click.echo("=" * 50)
    
    if "github" in data:
        click.echo("\nGitHub Repository:")
        click.echo(f"  Organización: {data['github']['org_name']}")
        click.echo(f"  Repository Name: {data['github']['repo_name']}")
        click.echo(f"  Description: {data['github'].get('description', '')}")
    
    if "workflow" in data:
        click.echo("\nWorkflow:")
        click.echo(f"  Workflow: {data['workflow']['workflow']}")
    
    # Add more sections here in the future
    click.echo()


@cli.command()
@click.option("--upgrade", is_flag=True, help="Actualiza a la última versión disponible desde el repositorio")
@click.argument("config", required=False)
def run(config, upgrade):
    """Execute provisioning based on the configuration file.
    
    CONFIG: Path to YAML configuration file (default: proyecto.yml)
    """
    # Si se solicita actualización manual, ejecutarla y salir
    if upgrade:
        upgrade_to_latest()
        return 0
    
    # Validar variables de entorno antes de continuar
    is_valid, error_message = validate_environment()
    if not is_valid:
        click.echo(f"\n✗ {error_message}", err=True)
        click.echo("\nPor favor, configura las variables de entorno necesarias antes de continuar.", err=True)
        sys.exit(1)

    config_file = None
    org_name = "ittidigital"  # Default
    original_config_file = None
    
    # Load config file path (if provided) - we'll use it but never modify it
    if config and os.path.exists(config):
        original_config_file = config
    else:
        # Use default config file if exists
        default_config = "proyecto.yml"
        if os.path.exists(default_config):
            original_config_file = default_config
    
    # Always collect user input interactively (repo_name always required)
    click.echo("🚀 Modo interactivo - Configuración de provisioning")
    data = collect_user_input()
    
    # Display summary and confirm
    display_summary(data)
    
    if not click.confirm("\n¿Confirmas estos datos? (Y/n)", default=True):
        click.echo("Operación cancelada.")
        return 1
    
    # If we have an original config file, load it and replace repo_name in memory only
    if original_config_file:
        try:
            with open(original_config_file, "r", encoding="utf-8") as file:
                config_dict = yaml.safe_load(file) or {}
            
            # Replace repo_name and description in memory only (for execution) - original file stays unchanged
            if "github" not in config_dict:
                config_dict["github"] = {}
            config_dict["github"]["repo_name"] = data["github"]["repo_name"]
            config_dict["github"]["description"] = data["github"]["description"]
            
            # Add workflow if not "No por ahora"
            if "workflow" in data and data["workflow"]["workflow"] != "No por ahora":
                config_dict["workflow"] = {
                    "type": data["workflow"]["workflow"]
                }
            
            # Create temporary YAML file with modified config (original file stays unchanged)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as tmp_file:
                yaml.dump(config_dict, tmp_file, default_flow_style=False, allow_unicode=True)
                config_file = tmp_file.name
        except Exception as e:
            click.echo(f"Error al procesar el archivo de configuración: {e}", err=True)
            return 1
    else:
        # Generate temporary config file from collected data
        config_dict = {
            "github": {
                "repo_name": data["github"]["repo_name"],
                "description": data["github"]["description"],
                "is_private": False,
            }
        }
        
        # Add workflow if not "No por ahora"
        if "workflow" in data and data["workflow"]["workflow"] != "No por ahora":
            config_dict["workflow"] = {
                "type": data["workflow"]["workflow"]
            }
        
        # Create temporary YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as tmp_file:
            yaml.dump(config_dict, tmp_file, default_flow_style=False, allow_unicode=True)
            config_file = tmp_file.name
    
    org_name = data["github"]["org_name"]

    try:
        gitHubToken = os.environ.get('ADP_GIT_HUB_TOKEN')
        # Initialize GitHub client with the selected organization
        gitHubClient = GitHubClient(token=gitHubToken, org_name=org_name)
        # Initialize orchestrator and execute provisioning
        orchestrator = Orchestrator(gitHubClient, config_file)
        orchestrator.provision()
        click.echo("\n✓ Provisioning completed successfully")
        
        # Clean up temporary config file if it was created (always cleanup since we always create a temp file)
        if config_file and os.path.exists(config_file):
            try:
                os.unlink(config_file)
            except Exception:
                pass
        
        return 0
    except Exception as e:
        click.echo(f"\n✗ Error during provisioning: {e}", err=True)
        
        # Clean up temporary config file on error
        if config_file and os.path.exists(config_file):
            try:
                os.unlink(config_file)
            except Exception:
                pass
        
        return 1


def main():
    """Main entry point."""
    # Verificar actualizaciones obligatoriamente antes de continuar
    # Esto asegura que siempre se ejecute la versión mandatoria
    # Se puede deshabilitar en desarrollo con la variable de entorno ADP_SKIP_VERSION_CHECK
    skip_check = os.getenv("ADP_SKIP_VERSION_CHECK", "").lower() in ("1", "true", "yes")
    
    if not skip_check:
        # Siempre verificar actualizaciones, tanto en modo instalado como desarrollo
        # Esto permite probar el sistema de actualización incluso en desarrollo
        try:
            check_for_updates()
        except SystemExit:
            # Si check_for_updates() hace sys.exit(), propagar el error
            raise
        except Exception as e:
            # Si hay algún error inesperado, mostrar el error pero no continuar
            print(f"ERROR: Error inesperado al verificar actualizaciones: {e}", file=sys.stderr)
            print("El programa no puede continuar sin verificar la versión mandatoria.", file=sys.stderr)
            sys.exit(1)
    
    sys.exit(cli())


if __name__ == "__main__":
    main()

