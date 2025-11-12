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
from .check_updates import check_for_updates


def get_version():
    """Get the current version of the package."""
    try:
        return version("adpcli")
    except PackageNotFoundError:
        return "#.#.#"  # Fallback version


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
@click.argument("config", required=False)
def run(config):
    """Execute provisioning based on the configuration file.
    
    CONFIG: Path to YAML configuration file (default: proyecto.yml)
    """

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
    # Solo verificar actualizaciones si se ejecuta desde el comando instalado,
    # no cuando se ejecuta desde el código fuente (modo desarrollo)
    # Verificamos si estamos ejecutando desde un paquete instalado
    try:
        import importlib.util
        main_file = importlib.util.find_spec("cli.main").origin
        # Si el archivo está en site-packages, es una instalación real
        if "site-packages" in main_file:
            check_for_updates()
    except Exception:
        # Si hay algún error o estamos en modo desarrollo, no verificar actualizaciones
        pass
    
    sys.exit(cli())


if __name__ == "__main__":
    main()

